"use client";

import React from "react";

export function AboutCard({
                            bio,
                            hostName,
                          }: {
  hostName: string;
  bio: string | null;
}) {

  return (
    <div className="px-4">
      <div className="group rounded-xl bg-background p-6 lg:p-10 flex flex-col gap-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-x-2 font-semibold text-lg lg:text-2xl">
            About {hostName}
          </div>
        </div>
        <p className="text-sm">
          {bio || ""}
        </p>
      </div>
    </div>
  );
}