import axios from "axios";
import {OngoingChatMessage, Role} from "@/components/stream-player/OngoingChatMessage"; // Ensure axios is imported
const BASE_URL = process.env.NEXT_PUBLIC_SERVER_URL;

export const getChatResponse = async (video_id: string,  newMessages: OngoingChatMessage[], query: string) => {
  try {
    const formattedMessages = [];

    let previousUserInput = '';

    for (const msg of newMessages.reverse()) {
      if (msg.role === Role.User) {
        previousUserInput = msg.message;
      }
      if (msg.role === Role.Assistant && previousUserInput) {
        formattedMessages.push({
          user_input: previousUserInput,
          assistant_response: msg.message
        });

        previousUserInput = '';
      }
    }

    const res = await axios.post(BASE_URL + `/chat/${video_id}`,
      { "message": query, "previous_messages": formattedMessages },
      {
        headers: { 'Content-Type': 'application/json' },
      });

    return res.data.answer;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw error;
    } else {
      throw new Error('different error than axios');
    }
  }
};