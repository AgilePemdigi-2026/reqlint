import { describe, expect, it, afterEach } from 'vitest';
import { translations, t, setUILocale, getUILocale } from './i18n';
import { EVALUATOR_OPTIONS, DEFAULT_EVALUATOR } from './evaluator-options';

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
  it('exposes exactly three selectable evaluators with rule_based default', () => {
    expect(EVALUATOR_OPTIONS.map((o) => o.id)).toEqual(['rule_based', 'traditional_ml', 'llm']);
    expect(DEFAULT_EVALUATOR).toBe('rule_based');
  });

  it('every option labelKey exists in the i18n dictionary', () => {
    for (const opt of EVALUATOR_OPTIONS) {
      expect(translations[opt.labelKey], opt.labelKey).toBeDefined();
    }
  });
});
