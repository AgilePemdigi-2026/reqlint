import { describe, expect, it, afterEach, beforeAll } from 'vitest';
import { translations, t, setUILocale, getUILocale } from './i18n';
import { resolveAiSuggestionStatus } from './ai-status';
import { buildExport, toMarkdown, toCsv } from './export';
import { loginSchema, registerSchema } from './validation';
import { categoryLabel, gradeLabel, gradeTagline, formatDate } from './format';
import { analyze } from './analyzer';

// The vitest suite runs in `environment: 'node'` (no window). The locale store
// falls back to the initial value whenever localStorage is unavailable, which
// would make locale-switch assertions meaningless — stub a minimal localStorage.
beforeAll(() => {
  const storage = new Map<string, string>();
  const localStorageStub = {
    getItem: (k: string) => storage.get(k) ?? null,
    setItem: (k: string, v: string) => void storage.set(k, v),
    removeItem: (k: string) => void storage.delete(k),
  };
  (globalThis as Record<string, unknown>).window = { localStorage: localStorageStub };
});

const story = 'Sebagai admin, saya ingin menghapus data dengan cepat agar hemat waktu.';
const result = analyze(story, 'id');
const revision = { text: story, changed: false, result, originalLocal: result };
const audit = {
  id: '1',
  seq: 1,
  title: 'Login cepat',
  text: story,
  createdAt: '2026-11-15T00:00:00Z',
  language: 'id' as const,
};

describe('i18n — Task 09 dictionary completeness', () => {
  it('every Task 09 namespace has both id and en translations', () => {
    const namespaces = [
      'landing.', 'demo.', 'editor.', 'history.', 'audit.', 'revision.', 'acceptance.',
      'diff.', 'scorecard.', 'summary.', 'findings.', 'auth.', 'fields.', 'reset.',
      'badge.', 'category.', 'grade.', 'tagline.', 'ai_status.', 'adapter.',
      'validation.', 'api.', 'llm_error.', 'nav.', 'general.',
    ];
    for (const [key, pair] of Object.entries(translations)) {
      if (!namespaces.some((n) => key.startsWith(n))) continue;
      expect(pair.id.trim(), `id of ${key}`).not.toBe('');
      expect(pair.en.trim(), `en of ${key}`).not.toBe('');
    }
  });

  it('every required page surface has its critical keys present', () => {
    const required = [
      // landing
      'landing.hero_title_1', 'landing.features_title', 'landing.faq_title', 'landing.cta_title',
      'landing.footer_product', 'landing.nav_start_free', 'landing.privacy_title',
      // demo
      'demo.analyze', 'demo.upload', 'demo.examples', 'demo.chars_suffix',
      // editor
      'editor.title', 'editor.run_audit', 'editor.hint_empty', 'editor.tip_title',
      'editor.evaluator_aria', 'editor.upload_pdf', 'editor.templates',
      // history
      'history.title', 'history.date_all', 'history.sort_newest', 'history.delete_all',
      'history.empty_title', 'history.open', 'history.delete_aria', 'history.search_sr',
      // audit
      'audit.title', 'audit.rerun', 'audit.export', 'audit.privacy_note', 'audit.loading_title',
      'audit.poll_stage1', 'audit.poll_stage2', 'audit.toast_copy_ok', 'audit.pipeline_pill',
      // components
      'revision.title', 'revision.empty', 'diff.pane_original', 'diff.removed',
      'scorecard.tooltip', 'summary.no_findings_aria', 'findings.clause', 'acceptance.note',
      // auth
      'auth.back_workspace', 'fields.show_password', 'reset.min_chars', 'reset.mismatch',
      'login.title', 'login.submit', 'register.title', 'register.submit',
      // shell & badge
      'nav.help', 'nav.contact', 'nav.main_nav_aria', 'nav.architecture',
      'badge.online', 'badge.offline', 'badge.checking',
      // labels
      'category.incomplete', 'grade.needs-improvement', 'tagline.poor',
      // AI status + adapter
      'ai_status.mock_desc', 'ai_status.provider_desc', 'adapter.invest_unknown',
      // validation
      'validation.email_required', 'validation.confirm_mismatch',
      // llm provider errors (all codes emitted by the backend)
      'llm_error.LLM_EVALUATOR_UNAVAILABLE', 'llm_error.ML_EVALUATOR_UNAVAILABLE',
      'llm_error.EVALUATION_FAILED', 'llm_error.LLM_PROVIDER_KEY_MISSING',
      'llm_error.LLM_PROVIDER_AUTH_FAILED', 'llm_error.LLM_MODEL_NOT_FOUND',
      'llm_error.LLM_RATE_LIMITED', 'llm_error.LLM_PROVIDER_TIMEOUT',
      'llm_error.LLM_PROVIDER_SERVER_ERROR', 'llm_error.LLM_INVALID_RESPONSE',
      'llm_error.LLM_PROVIDER_UNREACHABLE', 'llm_error.LLM_PROVIDER_REQUEST_REJECTED',
    ];
    for (const key of required) {
      expect(translations[key], `missing key ${key}`).toBeDefined();
    }
  });

  it('switching locale switches rendered text (spot checks on landing + editor)', () => {
    setUILocale('id');
    expect(t('editor.run_audit')).toBe('Audit User Story');
    setUILocale('en');
    expect(t('editor.run_audit')).toBe('Audit User Story');
    expect(t('landing.cta_signin')).toBe('Sign in');
    expect(t('history.delete_all')).toBe('Delete all');
    setUILocale('id');
    expect(t('history.delete_all')).toBe('Hapus semua');
  });

  afterEach(() => setUILocale('id'));
});

describe('Task 09 — localized helpers', () => {
  it('ai-status explanation follows the requested locale', () => {
    const detail = { ai_suggestion_source: 'mock' as const, status_audit: 'COMPLETED' as const, stage2_status: 'DONE' as const };
    const idStatus = resolveAiSuggestionStatus(detail, 'id');
    const enStatus = resolveAiSuggestionStatus(detail, 'en');
    expect(idStatus.explanation).toContain('bukan hasil model AI');
    expect(enStatus.explanation).toContain('not AI model output');
  });

  it('category, grade and tagline labels follow the locale', () => {
    expect(categoryLabel('incomplete', 'id')).toBe('Tidak Lengkap');
    expect(categoryLabel('incomplete', 'en')).toBe('Incomplete');
    expect(gradeLabel('needs-improvement', 'id')).toBe('Perlu Perbaikan');
    expect(gradeLabel('needs-improvement', 'en')).toBe('Needs Improvement');
    expect(gradeTagline('poor', 'id')).not.toBe(gradeTagline('poor', 'en'));
  });

  it('formatDate switches calendar locale', () => {
    // Same instant: ID uses Indonesian month abbreviations, EN uses English ones.
    expect(formatDate('2026-11-15T00:00:00Z', 'en')).toMatch(/Nov/);
    expect(formatDate('2026-11-15T00:00:00Z', 'id')).toMatch(/Nov/); // November shares the abbreviation
    expect(formatDate('2026-01-05T00:00:00Z', 'id')).toMatch(/Jan/);
    expect(formatDate('2026-02-05T00:00:00Z', 'en')).toMatch(/Feb/);
    // Indonesian February is "Feb", but August differs: Agu vs Aug.
    expect(formatDate('2026-08-05T00:00:00Z', 'id')).toMatch(/Agu/);
    expect(formatDate('2026-08-05T00:00:00Z', 'en')).toMatch(/Aug/);
  });

  it('validation schemas emit messages in the requested locale', () => {
    const en = loginSchema('en').safeParse({ email: '', password: '' });
    expect(en.error?.issues[0].message).toBe('Email is required.');
    const id = registerSchema('id').safeParse({ name: 'a', email: 'x@y.com', password: 'short', confirm: 'short', terms: true });
    expect(id.error?.issues.some((i) => i.message.includes('8 karakter'))).toBe(true);
    const mismatch = registerSchema('en').safeParse({ name: 'ab', email: 'x@y.com', password: 'Passw0rd1', confirm: 'Passw0rd2', terms: true });
    expect(mismatch.error?.issues[0].message).toBe('Password confirmation does not match.');
  });
});

describe('Task 09 — exports follow the UI locale (not the story language)', () => {
  it('markdown export with locale en uses English headings', () => {
    const md = toMarkdown(audit, result, revision, { locale: 'en' });
    expect(md).toContain('Audit Result 1');
    expect(md).toContain('## Defect Findings');
    expect(md).not.toContain('Temuan Cacat');
  });

  it('markdown export default (no meta) stays Indonesian for backward compatibility', () => {
    const md = toMarkdown(audit, result, revision);
    expect(md).toContain('Hasil Audit 1');
  });

  it('csv headers follow the locale', () => {
    const en = toCsv(audit, result, 'en');
    expect(en).toContain('"audit_id","clause","category"');
    const id = toCsv(audit, result, 'id');
    expect(id).toContain('"audit_id","kalimat","kategori"');
  });

  it('buildExport passes UI locale through to csv', () => {
    const csv = buildExport('csv', audit, result, revision, { locale: 'en' });
    expect(csv.content).toContain('"category"');
  });
});
