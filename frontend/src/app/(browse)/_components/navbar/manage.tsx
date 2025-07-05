import Image from "next/image";
import Link from "next/link";
import { Poppins } from "next/font/google";
import editIcon from "@/assets/images/edit.svg"

import { cn } from "@/lib/utils";

const font = Poppins({
  subsets: ["latin"],
  weight: ["200", "300", "400", "500", "600", "700", "800"],
});

export function ManageIcon() {
  return (
    <Link href="/manage">
      <div className="flex items-center gap-x-4 hover:opacity-75 transition">
        <Image src={editIcon} alt="edit" height="24" width="24" />
        <div className={cn(font.className, "hidden lg:block")}>
          <p className="text-xl font-semibold">Manage</p>
        </div>
      </div>
    </Link>
  );
}