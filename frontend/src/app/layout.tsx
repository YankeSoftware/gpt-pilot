import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'GPT Pilot UI',
  description: 'UI for managing GPT Pilot projects',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body 
        className="min-h-screen bg-gray-50"
        suppressHydrationWarning={true}
      >
        <div className="min-h-screen">
          {children}
        </div>
      </body>
    </html>
  )
}
