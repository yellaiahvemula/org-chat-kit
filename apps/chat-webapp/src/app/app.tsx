import { useCallback, useEffect, useState } from 'react';
import {
  chat,
  getBranding,
  getOrgs,
  llmStatus,
  type Branding,
  type ChatMessage,
  type LlmStatus,
} from '@org-chat-kit/chat-api-client';
import { Chat, ExpenseForm, LlmStatusPanel } from '@org-chat-kit/chat-ui';

type Tab = 'chat' | 'expense';

export function App() {
  const [orgs, setOrgs] = useState<string[]>([]);
  const [orgLabels, setOrgLabels] = useState<Record<string, string>>({});
  const [orgId, setOrgId] = useState('household');
  const [branding, setBranding] = useState<Branding | null>(null);
  const [status, setStatus] = useState<LlmStatus | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>('chat');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [busy, setBusy] = useState(false);
  const [flash, setFlash] = useState<string | null>(null);

  useEffect(() => {
    getOrgs()
      .then(async (r) => {
        setOrgs(r.orgs);
        const labels: Record<string, string> = {};
        await Promise.all(
          r.orgs.map(async (id) => {
            try {
              const b = await getBranding(id);
              labels[id] = b.display_name || id;
            } catch {
              labels[id] = id;
            }
          })
        );
        setOrgLabels(labels);
        if (r.orgs.includes('household')) setOrgId('household');
        else if (r.orgs[0]) setOrgId(r.orgs[0]);
      })
      .catch((e: Error) => setStatusError(e.message));
  }, []);

  useEffect(() => {
    if (!orgId) return;
    getBranding(orgId)
      .then(setBranding)
      .catch((e: Error) => setStatusError(e.message));
    setMessages([]);
    setTab('chat');
  }, [orgId]);

  const refreshStatus = useCallback(() => {
    llmStatus()
      .then((s) => {
        setStatus(s);
        setStatusError(null);
      })
      .catch((e: Error) => setStatusError(e.message));
  }, []);

  useEffect(() => {
    refreshStatus();
  }, [refreshStatus]);

  async function onSend(text: string) {
    setBusy(true);
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    try {
      const result = await chat(orgId, text);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: result.answer,
          tools: result.tools_used,
          confidence: result.confidence,
        },
      ]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: e instanceof Error ? e.message : String(e) },
      ]);
    } finally {
      setBusy(false);
      refreshStatus();
    }
  }

  const primary = branding?.primary_color ?? '#0f766e';
  const showExpense = orgId === 'household';

  return (
    <div className="layout" style={{ ['--accent' as string]: primary }}>
      <aside className="sidebar">
        <h1>Org Chat Kit</h1>
        <label>
          Organization
          <select value={orgId} onChange={(e) => setOrgId(e.target.value)}>
            {orgs.map((id) => (
              <option key={id} value={id}>
                {orgLabels[id] ?? id}
              </option>
            ))}
          </select>
        </label>
        {branding?.support_email && <p className="muted">{branding.support_email}</p>}
        <details open>
          <summary>LLM Status</summary>
          <LlmStatusPanel status={status} error={statusError} />
          <button type="button" className="linkish" onClick={refreshStatus}>
            Refresh
          </button>
        </details>
        <button type="button" onClick={() => setMessages([])}>
          Clear chat
        </button>
      </aside>

      <main className="main">
        <header className="main-header">
          <h2 style={{ color: primary }}>{branding?.display_name ?? 'Assistant'}</h2>
          <nav className="tabs">
            <button type="button" className={tab === 'chat' ? 'active' : ''} onClick={() => setTab('chat')}>
              Chat
            </button>
            {showExpense && (
              <button
                type="button"
                className={tab === 'expense' ? 'active' : ''}
                onClick={() => setTab('expense')}
              >
                Add expense
              </button>
            )}
          </nav>
        </header>

        {flash && <p className="flash">{flash}</p>}

        {tab === 'chat' ? (
          <Chat messages={messages} busy={busy} onSend={onSend} />
        ) : (
          <ExpenseForm
            onSaved={(msg) => {
              setFlash(msg);
              refreshStatus();
            }}
          />
        )}
      </main>
    </div>
  );
}

export default App;
