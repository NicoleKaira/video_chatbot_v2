"use client"

import ProtectedRoute from "@/hooks/protected-route"

export default function ManageLayout({
                                       children,
                                     }: {
  children: React.ReactNode
}) {
  return (
    <ProtectedRoute>
      {children}
    </ProtectedRoute>
  )
}