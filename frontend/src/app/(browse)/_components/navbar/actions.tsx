'use client'

import React, {useContext, useState} from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog";
import {Label} from "@/components/ui/label";
import {Input} from "@/components/ui/input";
import AuthContext from "@/hooks/auth";

export function Actions() {
  const { user, loginUser, logoutUser } = useContext(AuthContext);
  const [isDialogOpen, setDialogOpen] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  // Handle dialog open
  const handleLoginClick = () => {
    setDialogOpen(true);
  };

  const handleLogin = async () => {
    const data = await loginUser(username, password);
    console.log(data);
    if (data) {
      setDialogOpen(false);
      window.location.reload();
    }
  };

  const handleLogout = () => {
    logoutUser();
    window.location.reload();
  };

  return (
    <>
    <div className="flex items-center justify-end gap-x-2 ml-4 lg:ml-0">
      {user ? (
        <Button size="sm" variant="primary" onClick={handleLogout}>Logout</Button>
      ) : (
        <Button size="sm" variant="primary" onClick={handleLoginClick}>Login</Button>
      )}
    </div>

  <Dialog open={isDialogOpen} onOpenChange={setDialogOpen}>
    <DialogContent className="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>Login</DialogTitle>
        <DialogDescription>
          Login with your credentials.
        </DialogDescription>
      </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="username" className="text-right">
              Username
            </Label>
            <Input
              id="username"
              placeholder="Username"
              className="col-span-3"
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="password" className="text-right">
              Password
            </Label>
            <Input
              id="password"
              type={"password"}
              placeholder="Password"
              className="col-span-3"
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
        </div>
      <DialogFooter>
        <Button onClick={handleLogin} type="submit">Login</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
    </>
  );
}