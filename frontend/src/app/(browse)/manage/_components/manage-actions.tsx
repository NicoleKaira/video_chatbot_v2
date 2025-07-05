"use client"

import React, {useContext} from "react";

import {FileVideo , BookCheck, Upload} from "lucide-react"

import { ThumbnailSkeleton } from "@/components/thumbnail";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import {useSidebar} from "@/store/use-sidebar";
import AuthContext from "@/hooks/auth";

// Menu items.
const items = [
  {
    title: "Video",
    url: "/manage",
    icon: FileVideo ,
  },
  {
    title: "Course",
    url: "/manage/course",
    icon: BookCheck ,
  },
  {
    title: "Upload",
    url: "/manage/upload",
    icon: Upload ,
  }
]

export function ManageActions() {
  const { user } = useContext(AuthContext);
  const { collapsed } = useSidebar((state) => state);
  const role = user?.role ?? "";

  return (
    <div>
      {!collapsed && role === "ADMIN" && (
        <ul style={{listStyle: 'none', padding: 0}}>
          {items.map((item, index) => (
            <li
              key={index}
              className={"flex space-x-4 p-5"}
            >
              <item.icon />
              <Link
                href={item.url}
                className={"flex"}
              >
                {item.title}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function ResultCardSkeleton() {
  return (
    <div className="h-full w-full space-y-4">
      <ThumbnailSkeleton/>
      <div className="flex gap-x-3">
        <div className="flex flex-col gap-y-1">
          <Skeleton className="h-4 w-32"/>
          <Skeleton className="h-3 w-24"/>
        </div>
      </div>
    </div>
  );
}
