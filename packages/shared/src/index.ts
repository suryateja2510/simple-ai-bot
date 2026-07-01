export interface SharedChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: string;
}

export interface SharedSessionSummary {
  sessionId: string;
  title: string;
  createdAt: string;
}
