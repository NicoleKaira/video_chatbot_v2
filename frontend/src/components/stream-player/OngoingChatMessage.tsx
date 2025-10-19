export enum Role {
  User = "user",
  Assistant = "assistant",
  Loading = "loading",
}

export interface OngoingChatMessage {
  role: Role;
  message: string;
  timestamp: number;
}