import { useEffect, useMemo, useRef, useState } from 'react';
import { ChatSidebar } from './components/ChatSidebar';
import { ChatWindow } from './components/ChatWindow';
import { ChatInput } from './components/ChatInput';
import type { ChatMessage, ChatSession } from './types/chat';
import { createSession, fetchSession, fetchSessions, streamChat } from './services/api';

let sessionsLoaded = false;

function buildDisplayedMessages(messages: ChatMessage[], streamingText: string): ChatMessage[] {
  if (!streamingText) {
    return messages;
  }
  return [
    ...messages,
    {
      id: 'streaming-assistant',
      role: 'assistant',
      content: streamingText,
      createdAt: new Date().toISOString(),
    },
  ];
}

function App() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [streamingText, setStreamingText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [lastPayload, setLastPayload] = useState<string>('');
  const [lastEndpoint, setLastEndpoint] = useState<string>('');
  const [lastStatus, setLastStatus] = useState<number | null>(null);
  const [lastError, setLastError] = useState<string>('');
  const sendInProgressRef = useRef(false);
  const createSessionInProgressRef = useRef(false);

  const activeSession = useMemo(
    () => sessions.find((session) => session.sessionId === activeSessionId) ?? null,
    [activeSessionId, sessions],
  );

  useEffect(() => {
    if (sessionsLoaded) {
      return;
    }

    sessionsLoaded = true;
    let isMounted = true;
    async function loadSessions() {
      try {
        const data = await fetchSessions();
        if (isMounted) {
          setSessions(data);
          if (data.length > 0) {
            setActiveSessionId(data[0].sessionId);
          }
        }
      } catch (error) {
        console.error('Failed to load sessions:', error);
      }
    }

    loadSessions();
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (!activeSessionId) {
      setMessages([]);
      return;
    }

    let isMounted = true;
    async function loadSession(sessionId: string) {
      const session = await fetchSession(sessionId);
      if (isMounted) {
        setMessages(session.messages);
      }
    }

    loadSession(activeSessionId);
    return () => {
      isMounted = false;
    };
  }, [activeSessionId]);

  const displayedMessages = useMemo(
    () => buildDisplayedMessages(messages, streamingText),
    [messages, streamingText],
  );

  const createNewChat = async () => {
    if (createSessionInProgressRef.current) {
      return;
    }
    createSessionInProgressRef.current = true;
    try {
      const sessionId = await createSession();
      const newSession: ChatSession = {
        sessionId,
        title: 'New chat session',
        createdAt: new Date().toISOString(),
      };

      setSessions((current) => [newSession, ...current]);
      setActiveSessionId(sessionId);
      setStreamingText('');
      setMessages([]);
      setLastPayload('');
    } finally {
      createSessionInProgressRef.current = false;
    }
  };

  const handleSend = async () => {
    if (sendInProgressRef.current || !activeSessionId || !inputValue.trim()) {
      return;
    }

    sendInProgressRef.current = true;
    const question = inputValue.trim();
    const payload = { session_id: activeSessionId, user_input: question };
    setLastPayload(JSON.stringify(payload, null, 2));
    setLastEndpoint('/chat/stream');
    setLastStatus(null);
    setLastError('');
    setInputValue('');
    setStreamingText('');
    setIsStreaming(true);

    setMessages((current) => [
      ...current,
      {
        id: `user-${Date.now()}`,
        role: 'user',
        content: question,
        createdAt: new Date().toISOString(),
      },
    ]);

    let assistantText = '';
    try {
      const status = await streamChat(payload, (token) => {
        assistantText += token;
        setStreamingText((current) => current + token);
      });
      setLastStatus(status);
    } catch (error) {
      setLastError(error instanceof Error ? error.message : String(error));
    } finally {
      setIsStreaming(false);
      setStreamingText('');
      sendInProgressRef.current = false;
    }

    setMessages((current) => [
      ...current,
      {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: assistantText.trim(),
        createdAt: new Date().toISOString(),
      },
    ]);
  };

  return (
    <div className="h-screen bg-slate-950 text-slate-100">
      <div className="flex h-full gap-0">
        <ChatSidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelect={setActiveSessionId}
          onNewChat={createNewChat}
        />
        <main className="flex h-full min-w-0 flex-1 flex-col bg-slate-900 overflow-hidden">
          <div className="border-b border-slate-800 p-4">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div className="min-w-0">
                <h1 className="truncate text-2xl font-semibold">AI Chatbot</h1>
                <p className="mt-1 truncate text-sm text-slate-400">Ready for Azure service replacement.</p>
              </div>
              <div className="shrink-0 rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                {activeSession ? activeSession.title : 'No session'}
              </div>
            </div>
          </div>
          {!activeSessionId ? (
            <div className="flex flex-1 items-center justify-center p-10">
              <div className="w-full max-w-lg rounded-3xl border border-slate-800 bg-slate-950 p-10 text-center shadow-xl shadow-black/10">
                <h2 className="text-3xl font-semibold text-white">Welcome to AI Chatbot</h2>
                <p className="mt-4 text-slate-400">
                  Start a new conversation to chat with the AI. Your session will appear in the sidebar.
                </p>
                <button
                  onClick={createNewChat}
                  className="mt-8 rounded-2xl bg-indigo-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-indigo-500"
                >
                  New Chat
                </button>
              </div>
            </div>
          ) : (
            <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
              <ChatWindow messages={displayedMessages} isStreaming={isStreaming} />
              <div className="border-t border-slate-800 bg-slate-950">
                <ChatInput
                  value={inputValue}
                  onChange={setInputValue}
                  onSend={handleSend}
                  disabled={isStreaming || !activeSessionId}
                />
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
