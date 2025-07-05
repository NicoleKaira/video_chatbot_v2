import React, {useState} from "react";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {Visibility} from "@/model/Visibility";
import {Type} from "@/model/Course";
import visibilityChange from "@/api/visibility-change"
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel,
  AlertDialogContent, AlertDialogDescription, AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Link } from 'lucide-react';

export function SelectOptions({currentOption, type, id, disabled}: {
  currentOption: string,
  type: Type,
  id: string,
  disabled: boolean,
}) {
  const [option, setOption] = useState(currentOption);
  const [openDialog, setOpenDialog] = useState(false);
  const [openLinkDialog, setOpenLinkDialog] = useState(false); // State for the new dialog
  const [pendingOption, setPendingOption] = useState<string | null>(null);
  const [generatedLink, setGeneratedLink] = useState<string | null>(null);

// Function to handle visibility change and trigger the dialog
  const handleVisibilityChange = (newOption: string) => {
    setPendingOption(newOption); // Store the new option the user selected
    if (newOption === Visibility.RESTRICTED || newOption === Visibility.PUBLIC) {
      //TODO: API
      const link = "";
      setGeneratedLink(link); // Set the generated link
    } else {
      setGeneratedLink(null); // Clear the link for "Only Me"
    }
    setOpenDialog(true); // Open the dialog for confirmation
  };

  // Function to confirm visibility change
  const confirmChange = async () => {
    if (pendingOption) {
      console.log("Visibility changed to:", pendingOption);
      const data = await visibilityChange.triggerVisibilityChange(pendingOption, type, id);
      if (data.statusCode === 200) {
        setOption(pendingOption);
      }
    }
    setOpenDialog(false);
  };

  // Function to cancel visibility change
  const cancelChange = () => {
    setOpenDialog(false); // Close the dialog without making changes
  };

  // Function to open the link dialog
  const openCopyLinkDialog = () => {
    setOpenLinkDialog(true); // Open the link dialog
  };

  // Function to close the link dialog
  const closeCopyLinkDialog = () => {
    setOpenLinkDialog(false); // Close the link dialog
  };

  // Function to copy the link to clipboard
  const copyLinkToClipboard = () => {
    if (generatedLink) {
      navigator.clipboard.writeText(generatedLink).then(() => {
        alert("Link copied to clipboard!");
      }).catch(err => {
        alert("Failed to copy link: " + err);
      });
    }
  };

  return (
    <div>
    <Select value={option} onValueChange={handleVisibilityChange} disabled={disabled}>
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder={option} />
      </SelectTrigger>
      <SelectContent>
        {Object.values(Visibility).map((option) => (
          <SelectItem key={option} value={option}>{option}</SelectItem>
        ))}
      </SelectContent>
    </Select>

      {/* Show the link icon next to the Select component if the visibility is RESTRICTED or PUBLIC */}
      {generatedLink && (
        <div className="flex items-center space-x-2">
          <Link onClick={openCopyLinkDialog} size={20} /> {/* Link icon */}
        </div>
      )}

      <AlertDialog open={openDialog} onOpenChange={setOpenDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you absolutely sure you want to change visibility?</AlertDialogTitle>
            <AlertDialogDescription>
              <p>Public - Anyone can see</p>
              <p>Restricted - Only people with the link can see</p>
              <p>Only Me - Only you can see</p>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={cancelChange}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmChange}>Continue</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={openLinkDialog} onOpenChange={setOpenLinkDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Copy the Shareable Link</AlertDialogTitle>
          </AlertDialogHeader>
          <AlertDialogDescription>
            <p>Here is the link you can share with others:</p>
            {generatedLink && (
              <div className="mt-2">
                <input
                  type="text"
                  value={generatedLink}
                  readOnly
                  className="border p-2 w-full"
                />
              </div>
            )}
          </AlertDialogDescription>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={closeCopyLinkDialog}>Close</AlertDialogCancel>
            <AlertDialogAction onClick={copyLinkToClipboard}>Copy Link</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}