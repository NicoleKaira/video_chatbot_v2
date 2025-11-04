"use client"

import React from "react";

import {FileVideo , BookCheck, Upload, BotMessageSquare} from "lucide-react"

import { ThumbnailSkeleton } from "@/components/thumbnail";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import {useSidebar} from "@/store/use-sidebar";

// Menu items.
const items = [
  {
    title: "Course",
    url: "/manage/course",
    icon: BookCheck ,
  },
  {
    title: "Upload",
    url: "/manage/upload",
    icon: Upload ,
  },
  {
    title: "Video",
    url: "/manage",
    icon: FileVideo ,
  },
  {
    title: "Chat",
    url: "/manage/chat",
    icon: BotMessageSquare
  }
]

export function ManageActions() {
  const { collapsed } = useSidebar((state) => state);

  return (
    <div>
      {!collapsed && (
        <ul style={{listStyle: 'none', padding: 0}}>
          {items.map((item, index) => (
            <li
              key={index}
              className={"flex items-center space-x-4 p-5 hover:bg-accent rounded-lg cursor-pointer transition-colors"}
            >
              <item.icon className="w-5 h-5" />
              <Link
                href={item.url}
                className={"flex text-sm font-medium hover:text-primary"}
              >
                {item.title}
              </Link>
            </li>
          ))}
        </ul>
      )}
      {collapsed && (
        <ul style={{listStyle: 'none', padding: 0}}>
          {items.map((item, index) => (
            <li
              key={index}
              className={"flex items-center justify-center p-5 hover:bg-accent rounded-lg cursor-pointer transition-colors"}
              title={item.title}
            >
              <Link href={item.url}>
                <item.icon className="w-5 h-5" />
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
