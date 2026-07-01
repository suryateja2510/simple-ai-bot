import type { ChatMessage, ChatRequest, ChatSession, EpisodicMemory } from '../types/chat';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function createSession(): Promise<string> {
  const response = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) {
    throw new Error(`Failed to create session: ${response.status}`);
  }
  const data = await response.json();
  return data.session_id;
}

export async function fetchSessions(): Promise<ChatSession[]> {
  const response = await fetch(`${API_BASE}/sessions`);
  if (!response.ok) {
    throw new Error(`Failed to fetch sessions: ${response.status}`);
  }
  const data: Array<{ session_id: string; title: string; created_at: string }> = await response.json();
  return data.map(session => ({
    sessionId: session.session_id,
    title: session.title,
    createdAt: new Date(session.created_at).toISOString(),
  }));
}

export async function fetchSession(sessionId: string): Promise<{ sessionId: string; title: string; messages: ChatMessage[] }> {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch session: ${response.status}`);
  }
  const data: { session_id: string; title: string; messages: Array<{ role: string; content: string; created_at: string }>; created_at: string } = await response.json();
  return {
    sessionId: data.session_id,
    title: data.title,
    messages: data.messages.map((msg, idx) => ({
      id: `msg-${idx}`,
      role: msg.role as 'user' | 'assistant',
      content: msg.content,
      createdAt: new Date(msg.created_at).toISOString(),
    })),
  };
}

export async function streamChat(request: ChatRequest, onToken: (token: string) => void): Promise<number> {
  const url = `${API_BASE}/chat/stream`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  if (!response.body) {
    throw new Error(`No response body from ${url}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let done = false;

  while (!done) {
    const result = await reader.read();
    done = result.done ?? false;
    if (result.value) {
      onToken(decoder.decode(result.value));
    }
  }

  return response.status;
}

export async function fetchEpisodicMemory(): Promise<EpisodicMemory | null> {
  const response = await fetch(`${API_BASE}/memory/episodic`);
  if (!response.ok) {
    throw new Error(`Failed to fetch episodic memory: ${response.status}`);
  }
  const data: { user_id: string; memory: string; created_at: string } | null = await response.json();
  if (!data) {
    return null;
  }
  return {
    userId: data.user_id,
    memory: data.memory,
    createdAt: new Date(data.created_at).toISOString(),
  };
}

export async function upsertEpisodicMemory(memory: string): Promise<EpisodicMemory> {
  const response = await fetch(`${API_BASE}/memory/episodic`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ memory }),
  });
  if (!response.ok) {
    throw new Error(`Failed to update episodic memory: ${response.status}`);
  }
  const data: { user_id: string; memory: string; created_at: string } = await response.json();
  return {
    userId: data.user_id,
    memory: data.memory,
    createdAt: new Date(data.created_at).toISOString(),
  };
}
