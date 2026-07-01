import type { ChatSession } from '../types/chat';

interface ChatSidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelect: (id: string) => void;
  onNewChat: () => void;
}

export function ChatSidebar({ sessions, activeSessionId, onSelect, onNewChat }: ChatSidebarProps) {
  return (
    <aside className="w-72 shrink-0 border-r border-slate-800 bg-slate-950 p-4 flex min-h-screen flex-col">
      <div className="mb-4 flex items-center justify-between gap-2">
        <h2 className="truncate text-lg font-semibold">Conversations</h2>
        <button
          onClick={onNewChat}
          className="shrink-0 rounded bg-indigo-600 px-2 py-1 text-sm font-medium text-white hover:bg-indigo-500"
        >
          New
        </button>
      </div>
      <div className="flex-1 overflow-y-auto space-y-3 pr-1 pb-4">
        {sessions.map((session) => (
          <button
            key={session.sessionId}
            onClick={() => onSelect(session.sessionId)}
            className={`block w-full rounded border px-3 py-2 text-left transition ${
              session.sessionId === activeSessionId
                ? 'border-indigo-500 bg-slate-900'
                : 'border-slate-800 bg-slate-950 hover:border-slate-600'
            }`}
          >
            <div className="truncate font-semibold">{session.title}</div>
            <div className="truncate text-xs text-slate-500">{new Date(session.createdAt).toLocaleString()}</div>
          </button>
        ))}
      </div>
    </aside>
  );
}
