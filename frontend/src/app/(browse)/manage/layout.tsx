"use client"

// Authentication disabled - no protected routes

export default function ManageLayout({
                                       children,
                                     }: {
  children: React.ReactNode
}) {
  return (
    <>
      {children}
    </>
  )
}