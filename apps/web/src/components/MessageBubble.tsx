import type { ChatMessage } from '../types/chat';

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  return (
    <div className={`rounded-2xl p-4 ${isUser ? 'bg-slate-800 self-end' : 'bg-slate-900 self-start'}`}>
      <div className="text-sm leading-6">{message.content}</div>
    </div>
  );
}
