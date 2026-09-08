import type { LlmStatus } from '@org-chat-kit/chat-api-client';

type Props = {
  status: LlmStatus | null;
  error?: string | null;
};

export function LlmStatusPanel({ status, error }: Props) {
  if (error) {
    return <pre className="status-box error">{error}</pre>;
  }
  if (!status) {
    return <pre className="status-box muted">Loading LLM status…</pre>;
  }
  return <pre className="status-box">{JSON.stringify(status, null, 2)}</pre>;
}
