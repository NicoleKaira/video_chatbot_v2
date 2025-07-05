import { toast } from "sonner";
import { useRouter } from "next/router";
import { Button } from "@/components/ui/button";

function ErrorComponent({ error }: { error: string }) {
  const router = useRouter();

  // Show the toast
  toast.error("Error fetching video URL: " + error);

  return (
    <div className="flex flex-col items-center justify-center mt-6 space-y-4">
      <p className="text-red-500 font-medium">Something went wrong while loading the video.</p>
      <Button onClick={() => router.push("/")}>Return to Home</Button>
    </div>
  );
}
