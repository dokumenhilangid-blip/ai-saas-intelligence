export const metadata = {
  title: 'AI SaaS Intelligence',
  description: 'Market intelligence for AI SaaS tools',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={{
        margin: 0,
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
        backgroundColor: '#0a0a0a',
        color: '#ffffff'
      }}>
        {children}
      </body>
    </html>
  )
}
