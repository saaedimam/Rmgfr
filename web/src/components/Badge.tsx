// file: web/src/components/Badge.tsx
import React from "react"
export function Badge({ children }: { children: React.ReactNode }) {
  return <span className="inline-block rounded bg-gray-200 px-2 py-1 text-xs">{children}</span>
}
