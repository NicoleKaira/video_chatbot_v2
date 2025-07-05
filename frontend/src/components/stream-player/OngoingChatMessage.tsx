export enum Role {
  User = "user",
  Assistant = "assistant",
}

export interface OngoingChatMessage {
  role: Role;
  message: string;
  timestamp: number;
}