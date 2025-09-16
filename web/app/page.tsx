// file: web/app/page.tsx
import { Badge } from "@/components/Badge"
export default function Page() {
  return (
    <main className="p-8">
      <h1 className="text-2xl font-semibold">Anti-Fraud Platform</h1>
      <p className="mt-2 text-gray-600">Welcome. NEXT_PUBLIC_APP_NAME: {process.env.NEXT_PUBLIC_APP_NAME}</p>
      <div className="mt-4 space-x-2"><Badge>alpha</Badge><Badge>mvp</Badge></div>
    </main>
  )
}
