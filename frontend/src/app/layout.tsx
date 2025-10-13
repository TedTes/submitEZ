import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'  // ← This is critical!

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'SubmitEZ - AI-Powered Insurance Submission Automation',
  description:
    'Transform messy insurance documents into clean, validated submission packages with AI. Save 80% of data entry time.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        {children}
      </body>
    </html>
  )
}