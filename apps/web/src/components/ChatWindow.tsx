import { useEffect, useRef } from 'react';
import type { ChatMessage } from '../types/chat';
import { MessageBubble } from './MessageBubble';

interface ChatWindowProps {
  messages: ChatMessage[];
  isStreaming: boolean;
}

export function ChatWindow({ messages, isStreaming }: ChatWindowProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages, isStreaming]);

  return (
    <div ref={containerRef} className="flex h-full flex-col gap-4 overflow-y-auto p-6">
      <div className="space-y-4">
        {messages.map((message) => (
          <MessageBubble key={`${message.role}-${message.createdAt}`} message={message} />
        ))}
      </div>
      {isStreaming && <div className="text-slate-500">Typing...</div>}
    </div>
  );
}
