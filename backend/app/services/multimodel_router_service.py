"""Multi-Model White-Box & K-Means Scenario Router V2 inference service.

Loads the pre-trained bundle ``pm-docs/rubrics/models/reqlint_multimodel_router.pkl``
(produced by ``pm-docs/rubrics/train_multimodel_router.py``) and reproduces its
exact 18-feature extraction, TF-IDF backlog similarity, K-Means cluster routing,
per-cluster/per-criterion model selection, and Macro-F1 threshold comparison.
"""
import logging
import os
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.invest_ml_service import MLEvaluatorUnavailableError, TARGET_KEY_MAP
from app.services.story_parser import StoryParser

logger = logging.getLogger("reqlint.multimodel_router")

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


def strip_template(text: str) -> str:
    """Strip Connextra role/want prefix so similarity focuses on core capability."""
    t = str(text).strip()
    t = re.sub(r"(?i)^(sebagai|as a|as an)\s+[^,]+,?\s*", "", t)
    t = re.sub(r"(?i)^(saya ingin|i want to|i would like to|i need to|i want|ingin)\s+", "", t)
    return t.strip() if t.strip() else str(text).strip()


def _detect_lang(text: str) -> str:
    parsed = StoryParser.parse_structure(text)
    if parsed.get("lang") in ("id", "en"):
        return parsed["lang"]
    return "en"


def _tfidf_similarity_matrix(core_texts: Sequence[str]) -> np.ndarray:
    """Reproduce TF-IDF bigram cosine similarity from train_multimodel_router.py."""
    n = len(core_texts)
    if n <= 1:
        return np.zeros((n, n), dtype=float)
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1).fit_transform(core_texts)
    sim = cosine_similarity(vec)
    np.fill_diagonal(sim, 0.0)
    return sim


class MultiModelRouterService:
    """Genuine inference service for ``reqlint_multimodel_router.pkl`` (V2)."""

    _bundle: Optional[Dict[str, Any]] = None
    _loaded: bool = False

    DIRECT_MODEL_MAP: Dict[str, Tuple[str, str]] = {
        "v2_logistic_regression": ("LogisticRegression", "2.0-v2-logistic-regression"),
        "v2_decision_tree": ("DecisionTree", "2.0-v2-decision-tree"),
        "v2_complement_nb": ("ComplementNB", "2.0-v2-complement-nb"),
    }

    @classmethod
    def _load_bundle(cls) -> Optional[Dict[str, Any]]:
        if cls._loaded:
            return cls._bundle

        cls._loaded = True
        current_dir = os.path.dirname(os.path.abspath(__file__))
        candidate_paths = [
            os.path.abspath(
                os.path.join(current_dir, "..", "..", "..", "pm-docs", "rubrics", "models", "reqlint_multimodel_router.pkl")
            ),
            os.path.join(os.getcwd(), "pm-docs", "rubrics", "models", "reqlint_multimodel_router.pkl"),
            os.path.abspath(
                os.path.join(current_dir, "..", "..", "pm-docs", "rubrics", "models", "reqlint_multimodel_router.pkl")
            ),
        ]

        for path in candidate_paths:
            if os.path.exists(path):
                try:
                    import joblib

                    cls._bundle = joblib.load(path)
                    logger.info(f"Loaded Multi-Model Router V2 bundle from: {path}")
                    return cls._bundle
                except Exception as e:
                    logger.warning(f"Failed to load Multi-Model Router V2 bundle from {path}: {e}")

        logger.warning("Multi-Model Router V2 bundle not found.")
        return None

    @classmethod
    def extract_features_for_stories(
        cls,
        stories: Sequence[str],
        lexicon: Dict[str, Dict[str, str]],
        lang_code: Optional[str] = None,
    ) -> Tuple[np.ndarray, str]:
        """Extract the exact 18 white-box features for one or more stories in a draft."""
        texts = [str(s or "") for s in stories]
        if not texts:
            texts = [""]
        lang = lang_code or _detect_lang(texts[0])
        rules = lexicon.get(lang, lexicon.get("id", {}))

        core_texts = [strip_template(t) for t in texts]
        sim_matrix = _tfidf_similarity_matrix(core_texts)
        top_k = min(3, sim_matrix.shape[1])

        rows: List[List[float]] = []
        for idx, (text, core) in enumerate(zip(texts, core_texts)):
            row_sim = sim_matrix[idx]
            sorted_sim = np.sort(row_sim)[::-1]
            max_sim_backlog = float(row_sim.max()) if len(row_sim) else 0.0
            mean_top3_sim = float(sorted_sim[:top_k].mean()) if top_k > 0 else 0.0
            sim_over_05 = float((row_sim > 0.50).sum())
            max_sim_prev = float(sim_matrix[idx, :idx].max()) if idx > 0 else 0.0

            rows.append([
                float(len(text.split())),
                float(len(text)),
                float(len(core.split())),
                1.0 if re.search(rules["role"], text, re.IGNORECASE) else 0.0,
                1.0 if re.search(rules["want"], text, re.IGNORECASE) else 0.0,
                1.0 if re.search(rules["benefit"], text, re.IGNORECASE) else 0.0,
                float(len(re.findall(rules["conj"], text))),
                float(len(re.findall(r",", text))),
                float(len(re.findall(rules["ambiguous"], text))),
                float(len(re.findall(rules["abstract_verb"], text))),
                float(len(re.findall(rules["prescriptive"], text))),
                float(len(re.findall(rules["dependency_word"], text))),
                float(len(re.findall(rules["refinement_word"], core))),
                1.0 if re.search(r"\b\d+\b", text) else 0.0,
                max_sim_backlog,
                mean_top3_sim,
                sim_over_05,
                max_sim_prev,
            ])

        return np.array(rows, dtype=float), lang

    @classmethod
    def evaluate_story_router(cls, text: str) -> Dict[str, Any]:
        """Run genuine K-Means cluster routing and per-criterion white-box inference.

        Raises MLEvaluatorUnavailableError when the bundle is missing, malformed,
        or inference fails — never falls back to V1 or rule-based heuristics.
        """
        bundle = cls._load_bundle()
        try:
            if not isinstance(bundle, dict):
                raise MLEvaluatorUnavailableError(
                    "ML_EVALUATOR_UNAVAILABLE: Multi-Model Router V2 artifact is missing or corrupt."
                )

            required_keys = (
                "lexicon",
                "router_scaler",
                "kmeans_router",
                "cluster_labels",
                "routing_table",
                "thresholds",
                "models",
            )
            missing_keys = [k for k in required_keys if k not in bundle]
            if missing_keys:
                raise MLEvaluatorUnavailableError(
                    f"ML_EVALUATOR_UNAVAILABLE: Router V2 bundle missing keys: {missing_keys}"
                )

            parsed_stories = StoryParser.split_stories(text)
            story_texts = [s["text"] for s in parsed_stories] if parsed_stories else [text]
            X_all, detected_lang = cls.extract_features_for_stories(story_texts, bundle["lexicon"])

            # Route using the primary story (index 0) when evaluating a draft
            X_primary = X_all[:1]
            X_scaled = bundle["router_scaler"].transform(X_primary)
            cluster_id = int(bundle["kmeans_router"].predict(X_scaled)[0])
            cluster_labels = bundle["cluster_labels"]
            cluster_label = cluster_labels.get(cluster_id, f"Cluster {cluster_id}")

            routing_for_cluster = bundle["routing_table"].get(cluster_id, {})
            global_best = bundle.get("global_best", {})
            thresholds = bundle["thresholds"]
            models = bundle["models"]

            dimensions: Dict[str, Dict[str, Any]] = {}
            confidences: Dict[str, Optional[float]] = {}
            selected_models: Dict[str, str] = {}
            selected_thresholds: Dict[str, float] = {}

            for target_name, key in TARGET_KEY_MAP.items():
                chosen_model = routing_for_cluster.get(target_name) or global_best.get(target_name)
                if not chosen_model or target_name not in models or chosen_model not in models[target_name]:
                    raise MLEvaluatorUnavailableError(
                        f"ML_EVALUATOR_UNAVAILABLE: Router V2 missing model for {target_name}/{chosen_model}"
                    )

                model = models[target_name][chosen_model]
                threshold = float(thresholds.get(target_name, {}).get(chosen_model, 0.50))
                # For multi-story drafts, evaluate each story and average probability conservatively
                probas = [float(model.predict_proba(X_all[i : i + 1])[0][1]) for i in range(len(X_all))]
                proba = float(sum(probas) / len(probas))

                confidences[key] = round(proba, 4)
                selected_models[key] = chosen_model
                selected_thresholds[key] = threshold
                dimensions[key] = {
                    "label": "PASS" if proba >= threshold else "FAIL",
                    "confidence": confidences[key],
                    "rationale": f"routed to {chosen_model} (cluster {cluster_id}: {cluster_label}, threshold {threshold:.2f})",
                }

            version = str(bundle.get("version") or "2.0")
            return {
                "dimensions": dimensions,
                "confidences": confidences,
                "model_version": f"{version}-multimodel-router",
                "routing_metadata": {
                    "selection_mode": "auto_router",
                    "cluster_id": cluster_id,
                    "cluster_label": cluster_label,
                    "selected_models": selected_models,
                    "thresholds": selected_thresholds,
                    "language": detected_lang,
                    "story_count": len(story_texts),
                    "similarity_engine": "multilingual-e5-base" if bundle.get("use_e5") else "tfidf-bigram",
                },
            }
        except MLEvaluatorUnavailableError:
            raise
        except Exception as e:
            raise MLEvaluatorUnavailableError(
                f"ML_EVALUATOR_UNAVAILABLE: Multi-Model Router V2 inference failed: {e}"
            ) from e

    @classmethod
    def evaluate_story_direct(cls, text: str, ml_model: str) -> Dict[str, Any]:
        """Run genuine inference using a specific pre-trained V2 classifier directly.

        Preserves the exact 18-feature extraction, TF-IDF similarity, and
        per-criterion Macro-F1 thresholds from ``reqlint_multimodel_router.pkl``
        without K-Means routing or retraining.
        """
        if ml_model not in cls.DIRECT_MODEL_MAP:
            raise MLEvaluatorUnavailableError(
                f"ML_EVALUATOR_UNAVAILABLE: unknown V2 model {ml_model!r}"
            )
        clf_name, model_version = cls.DIRECT_MODEL_MAP[ml_model]
        bundle = cls._load_bundle()
        try:
            if not isinstance(bundle, dict):
                raise MLEvaluatorUnavailableError(
                    "ML_EVALUATOR_UNAVAILABLE: Multi-Model Router V2 artifact is missing or corrupt."
                )
            for req_key in ("lexicon", "thresholds", "models"):
                if req_key not in bundle:
                    raise MLEvaluatorUnavailableError(
                        f"ML_EVALUATOR_UNAVAILABLE: Router V2 bundle missing key: {req_key}"
                    )

            parsed_stories = StoryParser.split_stories(text)
            story_texts = [s["text"] for s in parsed_stories] if parsed_stories else [text]
            X_all, detected_lang = cls.extract_features_for_stories(story_texts, bundle["lexicon"])

            thresholds = bundle["thresholds"]
            models = bundle["models"]
            dimensions: Dict[str, Dict[str, Any]] = {}
            confidences: Dict[str, Optional[float]] = {}
            selected_models: Dict[str, str] = {}
            selected_thresholds: Dict[str, float] = {}

            for target_name, key in TARGET_KEY_MAP.items():
                if target_name not in models or clf_name not in models[target_name]:
                    raise MLEvaluatorUnavailableError(
                        f"ML_EVALUATOR_UNAVAILABLE: V2 bundle missing {clf_name} for {target_name}"
                    )
                model = models[target_name][clf_name]
                threshold = float(thresholds.get(target_name, {}).get(clf_name, 0.50))
                probas = [float(model.predict_proba(X_all[i : i + 1])[0][1]) for i in range(len(X_all))]
                proba = float(sum(probas) / len(probas))

                confidences[key] = round(proba, 4)
                selected_models[key] = clf_name
                selected_thresholds[key] = threshold
                dimensions[key] = {
                    "label": "PASS" if proba >= threshold else "FAIL",
                    "confidence": confidences[key],
                    "rationale": f"direct {clf_name} (V2, threshold {threshold:.2f})",
                }

            return {
                "dimensions": dimensions,
                "confidences": confidences,
                "model_version": model_version,
                "routing_metadata": {
                    "selection_mode": "direct",
                    "selected_model": clf_name,
                    "selected_models": selected_models,
                    "thresholds": selected_thresholds,
                    "language": detected_lang,
                    "story_count": len(story_texts),
                    "similarity_engine": "multilingual-e5-base" if bundle.get("use_e5") else "tfidf-bigram",
                },
            }
        except MLEvaluatorUnavailableError:
            raise
        except Exception as e:
            raise MLEvaluatorUnavailableError(
                f"ML_EVALUATOR_UNAVAILABLE: Direct V2 {clf_name} inference failed: {e}"
            ) from e

