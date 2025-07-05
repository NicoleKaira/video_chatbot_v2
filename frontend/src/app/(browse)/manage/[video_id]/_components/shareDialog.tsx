"use client"

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Copy } from "lucide-react"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"

type ShareDialogProps = {
  isDialogShareOpen: boolean
  id: string
  onOpenChange?: (open: boolean) => void
}

export const ShareDialog = ({ isDialogShareOpen, id, onOpenChange }: ShareDialogProps) => {
  const [url, setUrl] = useState("")
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (id) {
      const baseUrl = window.location.origin
      setUrl(`${baseUrl}/${id}`)
    }
  }, [id])

  const handleCopy = () => {
    navigator.clipboard.writeText(url)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <Dialog open={isDialogShareOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Share this URL with users to view the video:</DialogTitle>
        </DialogHeader>
        <div className="mt-2 flex items-center space-x-2">
          <Input readOnly value={url} className="cursor-text" />
          <Button onClick={handleCopy} variant="outline" size="icon">
            <Copy size={16} />
          </Button>
          {copied && <span className="text-sm text-green-500">Copied!</span>}
        </div>
      </DialogContent>
    </Dialog>
  )
}
