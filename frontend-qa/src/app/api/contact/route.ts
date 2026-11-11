import { NextResponse } from 'next/server';
import { contactSchema, fieldErrors } from '@/lib/validation';

/** Menerima pesan "Hubungi Kami". Saat ini hanya divalidasi dan dicatat di log server. */
export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: 'Body bukan JSON yang valid.' }, { status: 400 });
  }

  const parsed = contactSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ errors: fieldErrors(parsed.error) }, { status: 422 });
  }

  // TODO: kirim ke email / simpan ke database / teruskan ke backend FastAPI.
  console.info('[contact]', parsed.data.email, '-', parsed.data.subject);
  return NextResponse.json({ ok: true });
}