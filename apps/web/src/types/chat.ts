export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: string;
}

export interface ChatSession {
  sessionId: string;
  title: string;
  createdAt: string;
}

export interface CreateSessionResponse {
  sessionId: string;
}

export interface ChatRequest {
  session_id: string;
  user_input: string;
}

export interface EpisodicMemory {
  userId: string;
  memory: string;
  createdAt: string;
}
