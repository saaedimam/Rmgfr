import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ClerkProvider } from '@clerk/nextjs'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Platform Dashboard',
  description: 'Fraud/risk console',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className={inter.className} style={{margin:0}}>
          <div className="min-h-screen bg-background">
            {children}
          </div>
        </body>
      </html>
    </ClerkProvider>
  )
}
