import type { ChatMessage } from '@org-chat-kit/api-client';

type ChatProps = {
  messages: ChatMessage[];
  busy: boolean;
  onSend: (text: string) => void;
};

export function Chat({ messages, busy, onSend }: ChatProps) {
  return (
    <div className="chat">
      <div className="chat-messages">
        {messages.length === 0 && (
          <p className="muted">Ask about your documents. For household, add data via Add expense first.</p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`bubble bubble-${msg.role}`}>
            <div className="bubble-body">{msg.content}</div>
            {msg.role === 'assistant' && (msg.tools?.length || msg.confidence != null) && (
              <div className="bubble-meta">
                Tools: {(msg.tools ?? []).join(', ') || 'none'}
                {msg.confidence != null ? ` | Confidence: ${Math.round(msg.confidence * 100)}%` : ''}
              </div>
            )}
          </div>
        ))}
        {busy && <div className="muted">Thinking…</div>}
      </div>
      <form
        className="chat-form"
        onSubmit={(e) => {
          e.preventDefault();
          const form = e.currentTarget;
          const input = form.elements.namedItem('message') as HTMLInputElement;
          const text = input.value.trim();
          if (!text || busy) return;
          input.value = '';
          onSend(text);
        }}
      >
        <input name="message" placeholder="Type your question…" disabled={busy} autoComplete="off" />
        <button type="submit" disabled={busy}>
          Send
        </button>
      </form>
    </div>
  );
}
