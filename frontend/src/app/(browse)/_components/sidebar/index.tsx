"use client"

import React from "react";

import { Wrapper } from "./wrapper";
import { Toggle, ToggleSkeleton } from "./toggle";
import {ManageActions} from "@/app/(browse)/manage/_components/manage-actions";

export function Sidebar() {

  return (
    <Wrapper>
      <Toggle/>
      <ManageActions/>
    </Wrapper>
  );
}

export function SidebarSkeleton() {
  return (
    <aside className="fixed left-0 flex flex-col w-[70px] lg:w-60 h-full bg-background border-r border-[#2D2E35 z-50]">
      <ToggleSkeleton />
    </aside>
  );
}
