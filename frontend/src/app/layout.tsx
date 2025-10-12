import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Header } from '@/components/layout/Header'
import { Footer } from '@/components/layout/Footer'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'SubmitEZ - AI-Powered Insurance Submission Automation',
  description:
    'Transform messy insurance documents into clean, validated submission packages with AI. Save 80% of data entry time.',
  keywords: [
    'insurance',
    'submission',
    'automation',
    'AI',
    'ACORD forms',
    'commercial insurance',
    'insurance broker',
  ],
  authors: [{ name: 'SubmitEZ Team' }],
  creator: 'SubmitEZ',
  publisher: 'SubmitEZ',
  robots: 'index, follow',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://submitez.com',
    siteName: 'SubmitEZ',
    title: 'SubmitEZ - AI-Powered Insurance Submission Automation',
    description:
      'Transform messy insurance documents into clean, validated submission packages with AI.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'SubmitEZ',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'SubmitEZ - AI-Powered Insurance Submission Automation',
    description:
      'Transform messy insurance documents into clean, validated submission packages with AI.',
    images: ['/og-image.png'],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <div className="flex min-h-screen flex-col">
          <Header />
          <main className="flex-1">{children}</main>
          <Footer />
        </div>
      </body>
    </html>
  )
}