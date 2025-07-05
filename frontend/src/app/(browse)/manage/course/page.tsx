import React, { Suspense } from "react";
import { Metadata } from "next";

import { Results, ResultsSkeleton } from "./_components/results";

export const metadata: Metadata = {
  title: "CourseHome",
};

export default function CourseHome() {
  return (
    <div className="h-full p-8 max-w-screen-2xl mx-auto">
      <Suspense fallback={<ResultsSkeleton />}>
        <Results />
      </Suspense>
    </div>
  );
}
