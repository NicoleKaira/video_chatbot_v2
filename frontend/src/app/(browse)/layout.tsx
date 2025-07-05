'use client'

import React, {Suspense, useContext, useEffect, useState} from "react";

import { Container } from "./_components/container";
import { Navbar } from "./_components/navbar";
import { Sidebar, SidebarSkeleton } from "./_components/sidebar";
import AuthContext from "@/hooks/auth";

export default function BrowseLayout({
                                       children,
                                     }: {
  children: React.ReactNode;
}) {
  const { user } = useContext(AuthContext);

  return (
    <>
      <>
        <Navbar />
        <div className="flex h-full pt-20">
          {user && (
            <Suspense fallback={<SidebarSkeleton />}>
              <Sidebar />
            </Suspense>
          )}
          <Container>{children}</Container>
        </div>
      </>
    </>
  );
}