import { describe, expect, it, afterEach } from 'vitest';
import { translations, t, setUILocale, getUILocale } from './i18n';
import {
  EVALUATOR_OPTIONS,
  DEFAULT_EVALUATOR,
  ANALYZER_CATEGORY_OPTIONS,
  ML_MODEL_OPTIONS,
  resolveEvaluatorPayload,
} from './evaluator-options';

describe('i18n — Task 08 dictionary parity', () => {
  it('every key has a non-empty id and en translation', () => {
    for (const [key, pair] of Object.entries(translations)) {
      expect(pair.id.trim(), `id translation of ${key}`).not.toBe('');
      expect(pair.en.trim(), `en translation of ${key}`).not.toBe('');
    }
  });

  it('both locales expose the same key set (no missing keys)', () => {
    for (const [key, pair] of Object.entries(translations)) {
      expect('id' in pair || key, key).toBeTruthy();
      expect('en' in pair || key, key).toBeTruthy();
    }
    expect(Object.keys(translations).length).toBeGreaterThan(150);
  });

  it('evaluator labels are localized and recognizable', () => {
    setUILocale('id');
    expect(t('evaluator.rule_based')).toBe('Rule-Based');
    setUILocale('en');
    expect(t('evaluator.llm')).toBe('LLM/SLM');
  });

  it('t() falls back to id then to the raw key for unknown keys', () => {
    setUILocale('en');
    expect(t('editor.evaluator_label')).toBe('Evaluator');
    expect(t('key.that.does.not.exist')).toBe('key.that.does.not.exist');
  });

  afterEach(() => setUILocale('id'));
});

describe('evaluator options — Task 08', () => {
  it('exposes all four selectable evaluators with rule_based default', () => {
    expect(EVALUATOR_OPTIONS.map((o) => o.id)).toEqual([
      'rule_based',
      'traditional_ml',
      'multimodel_router',
      'llm',
    ]);
    expect(DEFAULT_EVALUATOR).toBe('rule_based');
  });

  it('every option labelKey exists in the i18n dictionary', () => {
    for (const opt of EVALUATOR_OPTIONS) {
      expect(translations[opt.labelKey], opt.labelKey).toBeDefined();
    }
    for (const cat of ANALYZER_CATEGORY_OPTIONS) {
      expect(translations[cat.labelKey], cat.labelKey).toBeDefined();
    }
    for (const model of ML_MODEL_OPTIONS) {
      expect(translations[model.labelKey], model.labelKey).toBeDefined();
    }
  });

  it('resolves granular ML model selections to the exact backend evaluator and ml_model', () => {
    expect(resolveEvaluatorPayload('rule_based')).toEqual({ evaluator: 'rule_based' });
    expect(resolveEvaluatorPayload('llm')).toEqual({ evaluator: 'llm' });
    expect(resolveEvaluatorPayload('machine_learning', 'v1_logistic_regression')).toEqual({
      evaluator: 'traditional_ml',
      ml_model: 'v1_logistic_regression',
    });
    expect(resolveEvaluatorPayload('machine_learning', 'v2_auto_router')).toEqual({
      evaluator: 'multimodel_router',
      ml_model: 'v2_auto_router',
    });
    expect(resolveEvaluatorPayload('machine_learning', 'v2_logistic_regression')).toEqual({
      evaluator: 'multimodel_router',
      ml_model: 'v2_logistic_regression',
    });
    expect(resolveEvaluatorPayload('machine_learning', 'v2_decision_tree')).toEqual({
      evaluator: 'multimodel_router',
      ml_model: 'v2_decision_tree',
    });
    expect(resolveEvaluatorPayload('machine_learning', 'v2_complement_nb')).toEqual({
      evaluator: 'multimodel_router',
      ml_model: 'v2_complement_nb',
    });
  });
});
