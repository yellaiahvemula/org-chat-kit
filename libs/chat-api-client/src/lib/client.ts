import type {
  Branding,
  Category,
  ChatResponse,
  ExpensePayload,
  ExpenseResult,
  LlmStatus,
} from './types';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export function getOrgs(): Promise<{ orgs: string[] }> {
  return request('/api/orgs');
}

export function getBranding(orgId: string): Promise<Branding> {
  return request(`/api/org/${encodeURIComponent(orgId)}/branding`);
}

export function chat(orgId: string, message: string): Promise<ChatResponse> {
  return request('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ org_id: orgId, message }),
  });
}

export function llmStatus(): Promise<LlmStatus> {
  return request('/api/llm/status');
}

export function listCategories(): Promise<{ categories: Category[] }> {
  return request('/api/household/categories');
}

export function addExpense(payload: ExpensePayload): Promise<ExpenseResult> {
  return request('/api/household/expenses', {
    method: 'POST',
    body: JSON.stringify({
      org_id: 'household',
      reingest: true,
      ...payload,
    }),
  });
}

export type {
  Branding,
  Category,
  ChatMessage,
  ChatResponse,
  ExpensePayload,
  ExpenseResult,
  LlmStatus,
} from './types';
