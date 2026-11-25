import type { EvaluatorId } from './api';

export const DEFAULT_EVALUATOR: EvaluatorId = 'rule_based';

export const EVALUATOR_OPTIONS: ReadonlyArray<{ id: EvaluatorId; labelKey: string }> = [
  { id: 'rule_based', labelKey: 'evaluator.rule_based' },
  { id: 'traditional_ml', labelKey: 'evaluator.traditional_ml' },
  { id: 'multimodel_router', labelKey: 'evaluator.multimodel_router' },
  { id: 'llm', labelKey: 'evaluator.llm' },
];

export type AnalyzerCategory = 'rule_based' | 'machine_learning' | 'llm';

export type MlModelId =
  | 'v1_logistic_regression'
  | 'v2_auto_router'
  | 'v2_logistic_regression'
  | 'v2_decision_tree'
  | 'v2_complement_nb';

export const DEFAULT_ML_MODEL: MlModelId = 'v1_logistic_regression';

export const ANALYZER_CATEGORY_OPTIONS: ReadonlyArray<{ id: AnalyzerCategory; labelKey: string }> = [
  { id: 'rule_based', labelKey: 'category.rule_based' },
  { id: 'machine_learning', labelKey: 'category.machine_learning' },
  { id: 'llm', labelKey: 'category.llm' },
];

export interface MlModelOption {
  id: MlModelId;
  group: 'ML V1' | 'ML V2';
  evaluator: 'traditional_ml' | 'multimodel_router';
  labelKey: string;
}

export const ML_MODEL_OPTIONS: ReadonlyArray<MlModelOption> = [
  {
    id: 'v1_logistic_regression',
    group: 'ML V1',
    evaluator: 'traditional_ml',
    labelKey: 'ml_model.v1_logistic_regression',
  },
  {
    id: 'v2_auto_router',
    group: 'ML V2',
    evaluator: 'multimodel_router',
    labelKey: 'ml_model.v2_auto_router',
  },
  {
    id: 'v2_logistic_regression',
    group: 'ML V2',
    evaluator: 'multimodel_router',
    labelKey: 'ml_model.v2_logistic_regression',
  },
  {
    id: 'v2_decision_tree',
    group: 'ML V2',
    evaluator: 'multimodel_router',
    labelKey: 'ml_model.v2_decision_tree',
  },
  {
    id: 'v2_complement_nb',
    group: 'ML V2',
    evaluator: 'multimodel_router',
    labelKey: 'ml_model.v2_complement_nb',
  },
];

export function resolveEvaluatorPayload(
  category: AnalyzerCategory,
  mlModel: MlModelId = DEFAULT_ML_MODEL,
): { evaluator: EvaluatorId; ml_model?: MlModelId } {
  if (category === 'rule_based') return { evaluator: 'rule_based' };
  if (category === 'llm') return { evaluator: 'llm' };
  const opt = ML_MODEL_OPTIONS.find((m) => m.id === mlModel) ?? ML_MODEL_OPTIONS[0];
  return { evaluator: opt.evaluator, ml_model: opt.id };
}
