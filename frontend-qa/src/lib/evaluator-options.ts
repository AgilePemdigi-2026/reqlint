import type { EvaluatorId } from './api';

export const DEFAULT_EVALUATOR: EvaluatorId = 'rule_based';

export const EVALUATOR_OPTIONS: ReadonlyArray<{ id: EvaluatorId; labelKey: string }> = [
  { id: 'rule_based', labelKey: 'evaluator.rule_based' },
  { id: 'traditional_ml', labelKey: 'evaluator.traditional_ml' },
  { id: 'llm', labelKey: 'evaluator.llm' },
];
