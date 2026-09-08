export type Branding = {
  name: string;
  display_name: string;
  language?: string;
  primary_color?: string;
  support_email?: string;
};

export type ChatResponse = {
  answer: string;
  confidence: number;
  escalated: boolean;
  tools_used: string[];
};

export type LlmStatus = {
  provider: string;
  llm_available: boolean;
  ollama_running: boolean;
  ollama_models?: string[];
  chat_model?: string;
  recommendations?: string[];
};

export type Category = {
  id: string;
  label: string;
};

export type ExpensePayload = {
  category: string;
  data: Record<string, string | number>;
  reingest?: boolean;
  org_id?: string;
};

export type ExpenseResult = {
  ok: boolean;
  file: string;
  chunks: number | null;
};

export type ChatMessage = {
  role: 'user' | 'assistant';
  content: string;
  tools?: string[];
  confidence?: number;
};
