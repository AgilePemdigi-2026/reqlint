import { NextResponse } from 'next/server';
import { analyze, revise } from '@/lib/analyzer';
import { analyzeRequestSchema, fieldErrors } from '@/lib/validation';

/**
 * POST /api/analyze  { "text": "...", "language": "id" | "en" }
 *
 * Endpoint untuk integrasi (CI, skrip, tool lain). UI web sendiri menjalankan mesin yang sama
 * langsung di browser sehingga draf pengguna tidak pernah dikirim ke server.
 */
export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: 'Body harus berupa JSON yang valid.' }, { status: 400 });
  }

  const parsed = analyzeRequestSchema('id').safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: 'Input tidak valid.', fields: fieldErrors(parsed.error) }, { status: 422 });
  }

  const { text, language } = parsed.data;
  const result = analyze(text, language);
  const revision = revise(text, language);

  return NextResponse.json({
    result,
    revision: { changed: revision.changed, text: revision.text, score: revision.result.score },
  });
}
