import os
import re
import glob
import joblib
import warnings
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import ComplementNB
from sklearn.cluster import KMeans
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.metrics import f1_score, accuracy_score, cohen_kappa_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

warnings.filterwarnings("ignore")

# =====================================================================
# 1. KONFIGURASI PATH & PARAMETER
# =====================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FOLDERS = {
    "id": r"D:\Kuliah\Semester 5\Pembangunan Perangkat Lunak - Prak\reqlint\pm-docs\rubrics\dataset-2-annotator\indo",
    "en": r"D:\Kuliah\Semester 5\Pembangunan Perangkat Lunak - Prak\reqlint\pm-docs\rubrics\dataset-2-annotator\eng",
}
MODEL_OUT_DIR = os.path.join(BASE_DIR, "models")
MODEL_OUT_PATH = os.path.join(MODEL_OUT_DIR, "reqlint_multimodel_router.pkl")

TARGET_COLS = ["y_I", "y_N", "y_V", "y_E", "y_S", "y_T"]
DIMS = ["I", "N", "V", "E", "S", "T"]
N_CLUSTERS = 3

# Otomatis pakai multilingual-e5-base jika sentence-transformers terpasang; jika tidak, fallback ke TF-IDF
USE_E5_EMBEDDING = True
_e5_model = None
_e5_warned = False

# =====================================================================
# 2. LAPISAN 1 & 3: EKSTRAKSI 18 FITUR DWIBAHASA (WHITE-BOX)
# =====================================================================
LEXICON = {
    "id": {
        "role": r"^\s*(sebagai)\b",
        "want": r"\b(saya ingin|ingin|saya mau|saya butuh|dapat)\b",
        "benefit": r"\b(agar|untuk|supaya|sehingga|guna)\b",
        "conj": r"\b(dan|serta|atau|maupun|sekaligus)\b",
        "ambiguous": r"\b(cepat|mudah|kustom|fleksibel|efisien|otomatis|sesuai|terkait|berbagai|optimal|baik|nyaman|aman|lengkap|sebanyak mungkin|sangat|jelas)\b",
        "abstract_verb": r"\b(memahami|mengetahui|tahu|merasakan|mengerti|memiliki|menggunakan)\b",
        "prescriptive": r"\b(frontend|backend|database|sql|tabel|button|tombol|dropdown|api|json|css|html|endpoint|klik|halaman|form|modal|csv|xml|ead|marcxml|pdf)\b",
        "dependency_word": r"\b(setelah|sebelum|jika sudah|bergantung pada|mengikuti|selama|ketika|saat)\b",
        "refinement_word": r"\b(hanya|kembali|ulang|mengulangi|mode|tertentu|kesalahan|error|tambahan|lanjutan|tersebut|itu|ini|lebih|juga|tetap|sudah ada|sebelumnya)\b",
    },
    "en": {
        "role": r"^\s*(as a|as an)\b",
        "want": r"\b(i want|i would like|i need|i can|to be able to)\b",
        "benefit": r"\b(so that|in order to|so i can|to ensure|to allow|to support)\b",
        "conj": r"\b(and|or|as well as|along with|plus)\b",
        "ambiguous": r"\b(fast|easy|easily|quickly|custom|flexible|efficient|automatic|appropriate|various|user-friendly|seamless|intuitive|properly|as much as possible|very|clearly)\b",
        "abstract_verb": r"\b(understand|know|feel|have|use|be aware)\b",
        "prescriptive": r"\b(frontend|backend|database|sql|table|button|dropdown|api|json|css|html|endpoint|click|page|form|modal|checkbox|csv|xml|ead|marcxml|pdf)\b",
        "dependency_word": r"\b(after|before|once|depending on|requires|during|when|while)\b",
        "refinement_word": r"\b(only|again|repeat|repeating|mode|specific|certain|error|additional|further|that|this|those|more|also|still|existing|previous|already)\b",
    },
}

FEATURE_NAMES = [
    "word_count",
    "char_count",
    "core_word_count",
    "has_role",
    "has_want",
    "has_benefit",
    "conj_count",
    "comma_count",
    "ambiguous_count",
    "abstract_verb_count",
    "prescriptive_count",
    "dependency_word_count",
    "refinement_word_count",
    "has_number_metric",
    "max_sim_backlog",
    "mean_top3_sim_backlog",
    "sim_over_05_count",
    "max_sim_prev_backlog",
]


def strip_template(text):
    """Menghapus frasa template 'Sebagai X, saya ingin...' agar kemiripan fokus pada inti fitur."""
    t = str(text).strip()
    t = re.sub(r"(?i)^(sebagai|as a|as an)\s+[^,]+,?\s*", "", t)
    t = re.sub(r"(?i)^(saya ingin|i want to|i would like to|i need to|i want|ingin)\s+", "", t)
    return t.strip() if t.strip() else str(text).strip()


def get_similarity_matrix(core_texts):
    """Menghitung kemiripan antar-story di dalam 1 backlog (e5 atau fallback TF-IDF)."""
    global _e5_model, _e5_warned
    if len(core_texts) <= 1:
        return np.zeros((len(core_texts), len(core_texts))), False

    if USE_E5_EMBEDDING:
        try:
            from sentence_transformers import SentenceTransformer
            if _e5_model is None:
                print("[Info] Memuat model semantik intfloat/multilingual-e5-base...")
                _e5_model = SentenceTransformer("intfloat/multilingual-e5-base")
            vecs = _e5_model.encode(["query: " + t for t in core_texts], normalize_embeddings=True)
            sim = vecs @ vecs.T
            np.fill_diagonal(sim, 0.0)
            return sim, True
        except ImportError:
            if not _e5_warned:
                print("[Info] sentence-transformers belum terpasang -> fallback ke Cleaned TF-IDF.")
                _e5_warned = True

    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1).fit_transform(core_texts)
    sim = cosine_similarity(vec)
    np.fill_diagonal(sim, 0.0)
    return sim, False


def extract_features_for_backlog(texts, lang_code):
    """Mengekstrak 18 fitur white-box untuk kumpulan story dalam 1 backlog."""
    rules = LEXICON.get(lang_code, LEXICON["id"])
    s = pd.Series(texts).fillna("").astype(str)
    s_core = s.apply(strip_template)

    feats = pd.DataFrame(index=s.index)
    feats["word_count"] = s.apply(lambda x: len(x.split()))
    feats["char_count"] = s.apply(len)
    feats["core_word_count"] = s_core.apply(lambda x: len(x.split()))
    feats["has_role"] = s.str.contains(rules["role"], case=False, regex=True).astype(int)
    feats["has_want"] = s.str.contains(rules["want"], case=False, regex=True).astype(int)
    feats["has_benefit"] = s.str.contains(rules["benefit"], case=False, regex=True).astype(int)
    feats["conj_count"] = s.str.count(rules["conj"])
    feats["comma_count"] = s.str.count(r",")
    feats["ambiguous_count"] = s.str.count(rules["ambiguous"])
    feats["abstract_verb_count"] = s.str.count(rules["abstract_verb"])
    feats["prescriptive_count"] = s.str.count(rules["prescriptive"])
    feats["dependency_word_count"] = s.str.count(rules["dependency_word"])
    feats["refinement_word_count"] = s_core.str.count(rules["refinement_word"])
    feats["has_number_metric"] = s.str.contains(r"\b\d+\b", regex=True).astype(int)

    # Lapisan 3: Kemiripan inti fitur di dalam backlog yang sama
    sim_matrix, used_e5 = get_similarity_matrix(s_core.tolist())
    feats["max_sim_backlog"] = sim_matrix.max(axis=1)
    sorted_sim = np.sort(sim_matrix, axis=1)[:, ::-1]
    top_k = min(3, sim_matrix.shape[1])
    feats["mean_top3_sim_backlog"] = sorted_sim[:, :top_k].mean(axis=1) if top_k > 0 else 0.0
    sim_thresh = 0.80 if used_e5 else 0.50
    feats["sim_over_05_count"] = (sim_matrix > sim_thresh).sum(axis=1)

    # Kemiripan tertinggi terhadap story yang muncul SEBELUMNYA di backlog (indikasi fitur turunan)
    max_prev = np.zeros(len(s_core))
    for i in range(1, len(s_core)):
        max_prev[i] = sim_matrix[i, :i].max()
    feats["max_sim_prev_backlog"] = max_prev

    return feats[FEATURE_NAMES], used_e5


# =====================================================================
# 3. PEMUATAN DATASET 2-ANOTATOR & COHEN'S KAPPA
# =====================================================================
def load_datasets():
    all_dfs, all_feats = [], []
    used_e5_flag = False

    for lang_code, folder_path in FOLDERS.items():
        if not os.path.exists(folder_path):
            print(f"[Peringatan] Folder tidak ditemukan: {folder_path}")
            continue

        for fpath in sorted(glob.glob(os.path.join(folder_path, "*.csv"))):
            df = pd.read_csv(fpath)
            if "text" not in df.columns:
                continue

            df["_file_name"] = os.path.basename(fpath)
            df["_lang"] = lang_code
            feats, used_e5_flag = extract_features_for_backlog(df["text"].tolist(), lang_code)

            all_dfs.append(df)
            all_feats.append(feats)

    if not all_dfs:
        raise RuntimeError("Tidak ada file CSV yang berhasil dibaca. Periksa kembali path folder!")

    full_df = pd.concat(all_dfs, ignore_index=True)
    full_X = pd.concat(all_feats, ignore_index=True)
    return full_df, full_X, used_e5_flag


def print_cohens_kappa(df_lab):
    print("\n=====================================================================")
    print(" 1. INTER-ANNOTATOR AGREEMENT (COHEN'S KAPPA: ANNOTATOR A vs B)")
    print("=====================================================================")
    has_ab = all(f"a_{d}" in df_lab.columns and f"b_{d}" in df_lab.columns for d in DIMS)
    if not has_ab:
        print("[Info] Kolom a_* / b_* tidak lengkap, melewati perhitungan Kappa.")
        return

    print(f"{'Kriteria':<10} | {'Kappa (All)':<12} | {'Kappa (ID)':<12} | {'Kappa (EN)':<12} | {'Status'}")
    print("-" * 70)

    for d in DIMS:
        sub = df_lab[[f"a_{d}", f"b_{d}", "_lang"]].dropna()
        if len(sub) == 0:
            continue

        def calc_k(frame):
            if len(frame) == 0:
                return 0.0
            a, b = frame[f"a_{d}"].astype(int), frame[f"b_{d}"].astype(int)
            if a.nunique() == 1 and b.nunique() == 1 and (a == b).all():
                return 1.0
            return cohen_kappa_score(a, b)

        k_all = calc_k(sub)
        k_id = calc_k(sub[sub["_lang"] == "id"])
        k_en = calc_k(sub[sub["_lang"] == "en"])
        status = "Almost Perfect" if k_all >= 0.81 else ("Substantial" if k_all >= 0.61 else "Moderate")
        print(f"y_{d:<8} | {k_all:<12.4f} | {k_id:<12.4f} | {k_en:<12.4f} | {status}")


# =====================================================================
# 4. MODEL POOL WHITE-BOX & AUTO-THRESHOLD TUNER (MACRO-F1)
# =====================================================================
def build_model_pool():
    pool = {
        "LogisticRegression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)),
        ]),
        "DecisionTree": DecisionTreeClassifier(
            max_depth=4, min_samples_leaf=5, class_weight="balanced", random_state=42
        ),
    }

    try:
        from interpret.glassbox import ExplainableBoostingClassifier
        pool["EBM"] = ExplainableBoostingClassifier(interactions=0, random_state=42)
    except ImportError:
        pool["ComplementNB"] = Pipeline([
            ("scaler", MinMaxScaler(clip=True)),
            ("clf", ComplementNB()),
        ])

    return pool


def find_optimal_threshold(y_true, probs):
    """Mencari threshold probabilitas terbaik berbasis Macro-F1 (mencegah prediksi 1 kelas saja)."""
    best_th = 0.50
    best_macro = -1.0
    for th in np.arange(0.35, 0.76, 0.02):
        preds = (probs >= th).astype(int)
        if len(np.unique(preds)) < 2:
            continue
        score = f1_score(y_true, preds, average="macro", zero_division=0)
        if score > best_macro:
            best_macro = score
            best_th = float(round(th, 2))
    return best_th


def describe_clusters(X_lab, clusters):
    df_c = X_lab.copy()
    df_c["_cluster"] = clusters
    summary = df_c.groupby("_cluster")[["word_count", "conj_count", "prescriptive_count", "max_sim_backlog"]].mean()

    labels = {}
    longest_c = summary["word_count"].idxmax()
    remaining = [c for c in summary.index if c != longest_c]
    tech_or_sim_c = summary.loc[remaining, ["prescriptive_count", "max_sim_backlog"]].sum(axis=1).idxmax()
    simple_c = [c for c in remaining if c != tech_or_sim_c][0]

    labels[int(simple_c)] = "Story Ringkas & Standar"
    labels[int(longest_c)] = "Story Panjang & Majemuk"
    labels[int(tech_or_sim_c)] = "Story Teknis / Tumpang Tindih"

    print("\n=====================================================================")
    print(" 2. PROFIL KLASTER SKENARIO (K-MEANS ROUTER)")
    print("=====================================================================")
    for cid in sorted(labels.keys()):
        row = summary.loc[cid]
        cnt = int((clusters == cid).sum())
        print(
            f" Klaster {cid} [{labels[cid]:<29}] (n={cnt:<3}) | "
            f"Avg Kata: {row['word_count']:4.1f} | Konjungsi: {row['conj_count']:.2f} | "
            f"Teknis: {row['prescriptive_count']:.2f} | MaxSim: {row['max_sim_backlog']:.2f}"
        )
    return labels


# =====================================================================
# 5. PIPELINE TRAINING V2, ROUTING TABLE & EKSPOR .PKL
# =====================================================================
def train_and_export():
    full_df, full_X, used_e5 = load_datasets()
    is_labeled = full_df[TARGET_COLS].notna().all(axis=1)

    df_lab = full_df[is_labeled].reset_index(drop=True)
    X_lab = full_X[is_labeled].reset_index(drop=True)
    n_unlab = int((~is_labeled).sum())

    print("=====================================================================")
    print(" REQLINT V2 — MULTI-MODEL WHITE-BOX & K-MEANS ROUTER TRAINER")
    print("=====================================================================")
    print(f" Total Baris       : {len(full_df)}")
    print(f" Data Berlabel     : {len(df_lab)} (ID: {(df_lab['_lang']=='id').sum()} | EN: {(df_lab['_lang']=='en').sum()})")
    print(f" Data Kosong (NaN) : {n_unlab} (disimpan untuk simulasi demo website)")
    print(f" Mode Kemiripan    : {'multilingual-e5-base (Semantik)' if used_e5 else 'Cleaned TF-IDF (Template-Stripped)'}")

    print_cohens_kappa(df_lab)

    # K-Means Scenario Router
    router_scaler = StandardScaler()
    X_scaled = router_scaler.fit_transform(X_lab)
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    cluster_labels = describe_clusters(X_lab, clusters)

    # Evaluasi Multi-Model dengan StratifiedGroupKFold + Threshold Tuning
    groups = df_lab["source_id"].astype(str) if "source_id" in df_lab.columns else pd.Series(range(len(df_lab)))
    model_names = list(build_model_pool().keys())

    trained_models = {col: {} for col in TARGET_COLS}
    thresholds = {col: {} for col in TARGET_COLS}
    routing_table = {cid: {} for cid in range(N_CLUSTERS)}
    global_best = {}

    print("\n==========================================================================================================")
    print(f" 3. PERBANDINGAN PERFORMA V2 (STRATIFIED GROUP 5-FOLD CV + THRESHOLD TUNING): {' vs '.join(model_names)}")
    print("==========================================================================================================")
    header_models = " | ".join([f"{m[:10]:<10}" for m in model_names])
    print(f"{'Kriteria':<8} | {header_models} | {'Router F1':<9} | {'Macro F1':<8} | {'Router Acc':<10} | {'Best (Th)'}")
    print("-" * 106)

    for col in TARGET_COLS:
        y = df_lab[col].astype(int)
        if y.nunique() < 2 or y.value_counts().min() < 2:
            print(f"{col:<8} | [Variasi kelas kurang — minimal 2 sampel per kelas]")
            continue

        n_splits = min(5, int(y.value_counts().min()))
        cv = StratifiedGroupKFold(n_splits=n_splits)

        oof_preds = {}
        global_f1s = {}
        global_macros = {}

        for mname, clf in build_model_pool().items():
            probs = cross_val_predict(clf, X_lab, y, cv=cv, groups=groups, method="predict_proba")[:, 1]
            opt_th = find_optimal_threshold(y, probs)
            preds = (probs >= opt_th).astype(int)

            thresholds[col][mname] = opt_th
            oof_preds[mname] = preds
            global_f1s[mname] = f1_score(y, preds, zero_division=0)
            global_macros[mname] = f1_score(y, preds, average="macro", zero_division=0)

            clf.fit(X_lab, y)
            trained_models[col][mname] = clf

        best_global_name = max(global_macros, key=global_macros.get)
        global_best[col] = best_global_name

        # Pilih Model Juara per Klaster berbasis Macro-F1 Out-of-Fold
        routed_oof = np.zeros(len(y), dtype=int)
        for cid in range(N_CLUSTERS):
            mask = (clusters == cid)
            if mask.sum() < 5 or y[mask].nunique() < 2:
                chosen = best_global_name
            else:
                cluster_scores = {
                    mname: f1_score(y[mask], oof_preds[mname][mask], average="macro", zero_division=0)
                    for mname in model_names
                }
                chosen = max(cluster_scores, key=cluster_scores.get)

            routing_table[cid][col] = chosen
            routed_oof[mask] = oof_preds[chosen][mask]

        router_f1 = f1_score(y, routed_oof, zero_division=0)
        router_macro = f1_score(y, routed_oof, average="macro", zero_division=0)
        router_acc = accuracy_score(y, routed_oof)

        f1_str = " | ".join([f"{global_f1s[m]:<10.3f}" for m in model_names])
        print(
            f"{col:<8} | {f1_str} | {router_f1:<9.3f} | {router_macro:<8.3f} | "
            f"{router_acc:<10.3f} | {best_global_name} ({thresholds[col][best_global_name]:.2f})"
        )

    print("\n=====================================================================")
    print(" 4. PETA ROUTING DINAMIS V2 (MODEL TERBAIK PER KLASTER & KRITERIA)")
    print("=====================================================================")
    for cid in range(N_CLUSTERS):
        route_str = ", ".join([f"{c.replace('y_', '')}:{routing_table[cid].get(c, '-')}" for c in TARGET_COLS])
        print(f" Klaster {cid} ({cluster_labels[cid]}):")
        print(f"   -> {route_str}")

    os.makedirs(MODEL_OUT_DIR, exist_ok=True)
    bundle = {
        "version": "2.0",
        "feature_names": FEATURE_NAMES,
        "lexicon": LEXICON,
        "router_scaler": router_scaler,
        "kmeans_router": kmeans,
        "cluster_labels": cluster_labels,
        "routing_table": routing_table,
        "thresholds": thresholds,
        "global_best": global_best,
        "models": trained_models,
        "model_names": model_names,
        "use_e5": used_e5,
    }
    joblib.dump(bundle, MODEL_OUT_PATH)
    print(f"\n[SUKSES] Bundle Multi-Model & Router V2 tersimpan di:\n  {MODEL_OUT_PATH}")


if __name__ == "__main__":
    train_and_export()