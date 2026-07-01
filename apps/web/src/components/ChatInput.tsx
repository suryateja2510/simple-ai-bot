interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled?: boolean;
}

export function ChatInput({ value, onChange, onSend, disabled = false }: ChatInputProps) {
  return (
    <div className="border-t border-slate-800 bg-slate-950 p-4">
      <div className="flex flex-row items-end gap-3">
        <textarea
          rows={2}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey && !disabled) {
              event.preventDefault();
              onSend();
            }
          }}
          className="flex-1 min-h-[80px] resize-none rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-indigo-500"
          placeholder="Ask a question..."
          disabled={disabled}
        />
        <button
          onClick={onSend}
          disabled={disabled || !value.trim()}
          className="shrink-0 h-[80px] w-32 rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition duration-150 hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-slate-700"
        >
          Send
        </button>
      </div>
    </div>
  );
}
