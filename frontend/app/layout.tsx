import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://chatdb-frontend.vercel.app'),
  title: {
    default: 'ChatDB - AI-Powered SQL Assistant',
    template: '%s | ChatDB',
  },
  description:
    'ChatDB is a production-ready AI-powered SQL assistant that enables non-technical users to query databases using natural language. Built with LangGraph, featuring multi-agent orchestration, RAG-powered schema discovery, and real-time streaming responses.',
  keywords: 'SQL assistant, natural language to SQL, database query, AI database, LangGraph, RAG, database interface, SQL generator, chat database, AI SQL, database assistant, query database',
  authors: { name: 'ChatDB Team' },
  creator: 'ChatDB',
  publisher: 'ChatDB',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '/',
    siteName: 'ChatDB',
    title: 'ChatDB - AI-Powered SQL Assistant',
    description:
      'Query your database using natural language. Production-ready AI assistant built with LangGraph, featuring multi-agent orchestration and RAG-powered schema discovery.',
    images: [
      {
        url: '/logo.png',
        width: 1200,
        height: 630,
        alt: 'ChatDB Logo',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ChatDB - AI-Powered SQL Assistant',
    description:
      'Query your database using natural language. Production-ready AI assistant built with LangGraph.',
    images: ['/logo.png'],
    creator: '@chatdb',
  },
  icons: {
    icon: [
      { url: '/icon.png', type: 'image/png' },
      { url: '/favicon.ico', sizes: 'any' },
    ],
    apple: [
      { url: '/icon.png', type: 'image/png' },
    ],
  },
  manifest: '/manifest.json',
  alternates: {
    canonical: '/',
  },
  category: 'technology',
};



export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}
