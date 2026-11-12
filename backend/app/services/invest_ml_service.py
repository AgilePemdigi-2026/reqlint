import os
import re
import logging
from typing import Dict, Any, List, Optional
import numpy as np

logger = logging.getLogger("reqlint.invest_ml")

# Regex patterns matching pm-docs/rubrics/coba 2.py
ROLE_PATTERN = re.compile(r'\b(sebagai|as a|as an)\b', re.I)
MEANS_PATTERN = re.compile(
    r'\b(saya ingin|saya mau|saya dapat|saya tidak ingin|saya harus|'
    r'i want|i would like|i can|i am able|i need|i should|i do not want|i don\'t want)\b', re.I
)
ENDS_PATTERN = re.compile(
    r'\b(sehingga|agar|supaya|untuk|karena|guna|'
    r'so that|in order to|so i can|because|to support|to allow|so as to)\b', re.I
)

PRESCRIPTIVE_PATTERN = re.compile(
    r'\b(tombol|kotak centang|checkbox|dropdown|klik|halaman|url|seo|wysiwyg|'
    r'html|csv|xml|marcxml|ead|eac-cpf|ldap|shibboleth|oai|stripe|pdf|gelang|'
    r'kalung|backend|frontend|database|basis data|api|navigasi berbasis papan ketik|'
    r'menyeret|button|click|page|table|modal|tab|drag and drop|dragging|keyboard|'
    r'bracelet|necklace|wristwatch)\b', re.I
)

VAGUE_PATTERN = re.compile(
    r'\b(mudah|cepat|bagus|jelas|sederhana|murah|mahal|fleksibel|tangguh|'
    r'komprehensif|efektif|efisien|ramah|otomatis|banyak|beberapa|berbagai|'
    r'sesuai kebutuhan|sebanyak mungkin|sesegera mungkin|tepat waktu|dll|dsb|'
    r'luar biasa|tidak memberi stigma|easy|easily|fast|quickly|good|nice|clear|clearly|'
    r'simple|cheap|flexible|robust|comprehensive|effective|efficient|various|multiple|'
    r'etc|as needed|as much as possible|as soon as possible|awesome|stigma)\b', re.I
)

DEPENDENCY_PATTERN = re.compile(
    r'\b(sebelumnya|tersebut|di atas|lainnya|lain|terkait|tambahan|kustom|'
    r'ulangi|mengulangi|terakhir|kedua|ketiga|kembali|lanjutan|sub-rekaman|'
    r'menimpa|mengoreksi|revisi|mengikat|daftar tunggu|previous|above|other|'
    r'related|additional|custom|repeat|last|second|third|return|refund|advanced|'
    r'sub-record|overwrite|revision|waitlist|waiting list|tie)\b', re.I
)

SUB_MODIFIER_PATTERN = re.compile(
    r'\b(hanya|secara tidak sengaja|ulang|massal|jika|ketika|saat|sebelum|'
    r'setelah|tanpa|terlepas|dengan menekan|dengan menyeret|atas nama|'
    r'only|accidentally|bulk|if|when|while|before|after|without|regardless|'
    r'on behalf of|by pressing|by dragging)\b', re.I
)

FOUNDATIONAL_ANCHOR_PATTERN = re.compile(
    r'\b(membuat dan mengedit|membuat dan memelihara|mengimpor data|mengimpor sumber daya|'
    r'mengimpor informasi|mengekspor rekaman|mengirimkan sesi|mengisi formulir pendaftaran|'
    r'membuat postingan blog|membuat koleksi|menerapkan atau menghapus embargo|'
    r'mengakses koleksi|mengunggah versi baru|menambahkan tanggal rilis|mengakses statistik|'
    r'menghubungi penulis|menayangkan media streaming|disimpan secara redundan|'
    r'masuk ke akun pribadi|menerima informasi|memperbesar konten visual|'
    r'memutuskan siapa yang memiliki akses|penghitung langkah|keadaan darurat|'
    r'menerima pengingat obat|berolahraga secara teratur|mengusulkan permainan|'
    r'panggilan bangun tidur|untuk navigasi|memelihara daftar kontak|'
    r'menyalakan/mematikan lampu|mencantumkan informasi dasar|tingkat sponsorship|'
    r'melihat daftar sponsor|memposting lowongan kerja|'
    r'create and edit|create and maintain|import accession|import resource|import agent|'
    r'export agent|submit a session|fill out a user registration|create a blog post|'
    r'create a collection|apply or remove access embargo|access collections|'
    r'upload a new version|add future release dates|access useful and comprehensive usage|'
    r'contact the author|stream media|redundantly stored|log into a personal account|'
    r'receive information from alfred|magnify visual content|decide who has access|'
    r'step counter|call help in case of an emergency|medicine reminders|'
    r'remind people to exercise regularly|propose games to me that require a combination|'
    r'wake-up call|use alfred for navigation|maintain my contact list|switch on/off the lights|'
    r'list basic information about my summit|learn about sponsorship levels|'
    r'see a list of sponsors|post a job listing)\b', re.I
)

TECH_TASK_PATTERN = re.compile(
    r'\b(perubahan backend|perubahan frontend|konfigurasi yang tidak dikemas|'
    r'pengimpor kustom|backend changes|frontend changes|unpackaged configuration|'
    r'custom importer)\b', re.I
)

EPIC_BROAD_PATTERN = re.compile(
    r'\b(semua|segala|segalanya|apa pun|berbagai|beberapa|komprehensif|seluruh|'
    r'setiap|all|everything|anything|various|multiple|comprehensive|entire|every)\b', re.I
)

CONJUNCTION_PATTERN = re.compile(
    r'\b(dan|serta|atau|maupun|dan/atau|sekaligus|sembari|sambil|'
    r'and|or|as well as|while|and/or)\b|,', re.I
)

NUMBER_METRIC_PATTERN = re.compile(
    r'(\d+|\$[0-9]+|1gb|satu|dua|tiga|one|two|three)', re.I
)

FEATURE_NAMES = [
    'word_count',
    'has_role',
    'has_means',
    'has_ends',
    'prescriptive_count',
    'vague_count',
    'dependency_word_count',
    'conjunction_count',
    'has_number_metric',
    'is_tech_task',
    'foundational_anchor_flag',
    'sub_modifier_count',
    'epic_broad_count',
    'max_sim_backlog',
    'mean_top3_sim_backlog',
    'sim_over_03_count',
    'cat_size',
    'rel_pos_in_cat',
    'is_first_in_cat',
    'max_sim_prev_in_cat',
    'mean_sim_prev_in_cat',
    'max_sim_in_cat',
    'is_most_central_in_cat',
]

TARGET_KEY_MAP = {
    'y_I': 'independent',
    'y_N': 'negotiable',
    'y_V': 'valuable',
    'y_E': 'estimable',
    'y_S': 'small',
    'y_T': 'testable'
}

class InvestMLService:
    _bundle: Optional[Dict[str, Any]] = None
    _loaded: bool = False

    @classmethod
    def _load_model_bundle(cls) -> Optional[Dict[str, Any]]:
        if cls._loaded:
            return cls._bundle

        cls._loaded = True
        current_dir = os.path.dirname(os.path.abspath(__file__))
        candidate_paths = [
            os.path.abspath(os.path.join(current_dir, "..", "..", "..", "pm-docs", "rubrics", "reqlint_invest_models.pkl")),
            os.path.abspath(os.path.join(current_dir, "..", "..", "..", "pm-docs", "rubrics", "models", "reqlint_invest_models.pkl")),
            os.path.join(os.getcwd(), "pm-docs", "rubrics", "reqlint_invest_models.pkl"),
            os.path.join(os.getcwd(), "pm-docs", "rubrics", "models", "reqlint_invest_models.pkl"),
        ]

        for path in candidate_paths:
            if os.path.exists(path):
                try:
                    import joblib
                    cls._bundle = joblib.load(path)
                    logger.info(f"Loaded INVEST ML models bundle from: {path}")
                    return cls._bundle
                except Exception as e:
                    logger.warning(f"Failed to load INVEST ML model from {path}: {e}")

        logger.info("INVEST ML model bundle not found; continuing with rule-based heuristics.")
        return None

    @classmethod
    def extract_features(cls, text: str) -> List[float]:
        t = str(text or "")
        words = t.split()
        word_count = float(len(words))

        has_role = 1.0 if ROLE_PATTERN.search(t) else 0.0
        has_means = 1.0 if MEANS_PATTERN.search(t) else 0.0
        has_ends = 1.0 if ENDS_PATTERN.search(t) else 0.0

        prescriptive_count = float(len(PRESCRIPTIVE_PATTERN.findall(t)))
        vague_count = float(len(VAGUE_PATTERN.findall(t)))
        dependency_word_count = float(len(DEPENDENCY_PATTERN.findall(t)))
        conjunction_count = float(len(CONJUNCTION_PATTERN.findall(t)))
        has_number_metric = 1.0 if NUMBER_METRIC_PATTERN.search(t) else 0.0
        is_tech_task = 1.0 if TECH_TASK_PATTERN.search(t) else 0.0
        foundational_anchor_flag = 1.0 if FOUNDATIONAL_ANCHOR_PATTERN.search(t) else 0.0
        sub_modifier_count = float(len(SUB_MODIFIER_PATTERN.findall(t)))
        epic_broad_count = float(len(EPIC_BROAD_PATTERN.findall(t)))

        # Default similarity context values for single-story real-time queries
        max_sim_backlog = 0.0
        mean_top3_sim_backlog = 0.0
        sim_over_03_count = 0.0
        cat_size = 1.0
        rel_pos_in_cat = 0.0
        is_first_in_cat = 1.0
        max_sim_prev_in_cat = 0.0
        mean_sim_prev_in_cat = 0.0
        max_sim_in_cat = 0.0
        is_most_central_in_cat = 1.0

        return [
            word_count,
            has_role,
            has_means,
            has_ends,
            prescriptive_count,
            vague_count,
            dependency_word_count,
            conjunction_count,
            has_number_metric,
            is_tech_task,
            foundational_anchor_flag,
            sub_modifier_count,
            epic_broad_count,
            max_sim_backlog,
            mean_top3_sim_backlog,
            sim_over_03_count,
            cat_size,
            rel_pos_in_cat,
            is_first_in_cat,
            max_sim_prev_in_cat,
            mean_sim_prev_in_cat,
            max_sim_in_cat,
            is_most_central_in_cat,
        ]

    @classmethod
    def evaluate_story(cls, text: str) -> Dict[str, Any]:
        bundle = cls._load_model_bundle()
        feat_vector = cls.extract_features(text)

        if not bundle or "models" not in bundle:
            # Fallback heuristic using rule extraction
            return {
                "independent": feat_vector[6] == 0.0,
                "negotiable": feat_vector[4] == 0.0,
                "valuable": feat_vector[9] == 0.0 and (feat_vector[1] + feat_vector[2] + feat_vector[3] >= 2),
                "estimable": feat_vector[5] == 0.0 and feat_vector[12] == 0.0,
                "small": feat_vector[7] <= 2.0 and feat_vector[12] == 0.0,
                "testable": feat_vector[5] == 0.0 and (feat_vector[8] == 1.0 or feat_vector[5] == 0.0),
                "probabilities": {}
            }

        models = bundle.get("models", {})
        X = np.array([feat_vector])

        results = {}
        probs = {}

        for target_name, key in TARGET_KEY_MAP.items():
            model = models.get(target_name)
            if model is None:
                # P0/ML-07: a missing model is an UNKNOWN state, not a pass.
                results[key] = None
                continue
            try:
                pred = int(model.predict(X)[0])
                results[key] = bool(pred == 1)
                if hasattr(model, "predict_proba"):
                    proba = float(model.predict_proba(X)[0][1])
                    probs[key] = round(proba, 3)
            except Exception as e:
                # P0/ML-07: fail closed — surface the failure instead of
                # fabricating a passing evaluation.
                logger.warning(f"Prediction failed for {target_name}: {e}")
                raise

        results["probabilities"] = probs
        return results
