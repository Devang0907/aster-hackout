import { post } from "./api";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export interface ChatRequest {
  message: string;
  history: ChatMessage[];
}

export interface ChatResponse {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export async function sendMessage(message: string, history: ChatMessage[]): Promise<ChatResponse> {
  const response = await post("/api/v1/chat/send", {
    message,
    history,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to send message");
  }

  return response.json();
}
