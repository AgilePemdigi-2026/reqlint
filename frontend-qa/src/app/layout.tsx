import type { Metadata, Viewport } from 'next';
import './globals.css';
import { Providers } from '@/components/providers';
import { LocaleHtmlSync } from '@/components/locale-html-sync';

export const metadata: Metadata = {
  title: { default: 'ReqLint — Audit Kualitas User Story', template: '%s · ReqLint' },
  description: 'Analisis kualitas User Story dengan enam dimensi INVEST (penilaian heuristik).',
  icons: { icon: '/favicon.svg' },
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#f1f1f6' },
    { media: '(prefers-color-scheme: dark)', color: '#0c0c10' },
  ],
};

// Terapkan tema tersimpan sebelum render pertama agar tidak berkedip.
const themeScript = `try{if(JSON.parse(localStorage.getItem('reqlint.theme'))==='dark')document.documentElement.classList.add('dark')}catch(e){}`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>
        <Providers>
          {/* Task 09: sinkronkan <html lang> dengan locale UI terpilih. */}
          <LocaleHtmlSync />
          {children}
        </Providers>
      </body>
    </html>
  );
}
