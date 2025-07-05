"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import useAuth from "@/hooks/use-auth";

type ProtectedRouteProps = {
  children: React.ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter()
  const { user, loading } = useAuth()

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/")
    }
  }, [user, loading, router])

  if (loading || !user) {
    return null
  }

  return <>{children}</>
}
