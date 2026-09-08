import { useEffect, useMemo, useState, type FormEvent } from 'react';
import { addExpense, listCategories, type Category } from '@org-chat-kit/api-client';

type Props = {
  onSaved?: (message: string) => void;
};

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function monthIso() {
  return new Date().toISOString().slice(0, 7);
}

export function ExpenseForm({ onSaved }: Props) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [category, setCategory] = useState('home_loan');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fields, setFields] = useState<Record<string, string>>({});

  useEffect(() => {
    listCategories()
      .then((r) => {
        setCategories(r.categories);
        if (r.categories[0]) setCategory(r.categories[0].id);
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  const fieldDefs = useMemo(() => fieldsForCategory(category), [category]);

  useEffect(() => {
    const next: Record<string, string> = {};
    for (const f of fieldsForCategory(category)) {
      next[f.key] = f.defaultValue;
    }
    setFields(next);
  }, [category]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const data: Record<string, string | number> = {};
      for (const f of fieldDefs) {
        const raw = fields[f.key] ?? '';
        data[f.key] = f.type === 'number' ? Number(raw || 0) : raw;
      }
      const result = await addExpense({ category, data, reingest: true });
      const msg = `Saved to ${result.file}${
        result.chunks != null ? ` — indexed ${result.chunks} chunks` : ''
      }.`;
      onSaved?.(msg);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="expense-form" onSubmit={submit}>
      <p className="muted">Writes a row into the matching markdown file, then re-ingests for RAG.</p>
      <label>
        Category
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.label}
            </option>
          ))}
        </select>
      </label>
      {fieldDefs.map((f) => (
        <label key={f.key}>
          {f.label}
          {f.type === 'select' ? (
            <select
              value={fields[f.key] ?? ''}
              onChange={(e) => setFields((prev) => ({ ...prev, [f.key]: e.target.value }))}
            >
              {(f.options ?? []).map((o) => (
                <option key={o} value={o}>
                  {o}
                </option>
              ))}
            </select>
          ) : (
            <input
              type={f.type === 'number' ? 'number' : 'text'}
              value={fields[f.key] ?? ''}
              onChange={(e) => setFields((prev) => ({ ...prev, [f.key]: e.target.value }))}
              step={f.type === 'number' ? 'any' : undefined}
            />
          )}
        </label>
      ))}
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={busy}>
        {busy ? 'Saving…' : 'Save expense'}
      </button>
    </form>
  );
}

type FieldDef = {
  key: string;
  label: string;
  type: 'text' | 'number' | 'select';
  defaultValue: string;
  options?: string[];
};

function fieldsForCategory(category: string): FieldDef[] {
  switch (category) {
    case 'home_loan':
      return [
        { key: 'month', label: 'Month (YYYY-MM)', type: 'text', defaultValue: monthIso() },
        { key: 'amount', label: 'EMI paid (INR)', type: 'number', defaultValue: '45000' },
        { key: 'principal', label: 'Principal (optional)', type: 'text', defaultValue: '' },
        { key: 'interest', label: 'Interest (optional)', type: 'text', defaultValue: '' },
        { key: 'notes', label: 'Notes', type: 'text', defaultValue: 'Auto-debit' },
      ];
    case 'credit_card':
      return [
        { key: 'card', label: 'Card label', type: 'text', defaultValue: 'Card A (1234)' },
        { key: 'amount', label: 'Statement amount (INR)', type: 'number', defaultValue: '0' },
        { key: 'minimum_due', label: 'Minimum due', type: 'text', defaultValue: '' },
        { key: 'paid', label: 'Paid?', type: 'select', defaultValue: 'Pending', options: ['Pending', 'Paid'] },
        { key: 'notes', label: 'Notes', type: 'text', defaultValue: '' },
      ];
    case 'gas':
      return [
        { key: 'month', label: 'Month (YYYY-MM)', type: 'text', defaultValue: monthIso() },
        { key: 'amount', label: 'Amount (INR)', type: 'number', defaultValue: '0' },
        { key: 'due_date', label: 'Due date (YYYY-MM-DD)', type: 'text', defaultValue: '' },
        { key: 'paid', label: 'Paid?', type: 'select', defaultValue: 'Pending', options: ['Pending', 'Paid'] },
        { key: 'provider', label: 'Provider', type: 'text', defaultValue: '' },
        { key: 'notes', label: 'Notes', type: 'text', defaultValue: '' },
      ];
    case 'electricity':
      return [
        { key: 'month', label: 'Month (YYYY-MM)', type: 'text', defaultValue: monthIso() },
        { key: 'units', label: 'Units', type: 'number', defaultValue: '0' },
        { key: 'amount', label: 'Amount (INR)', type: 'number', defaultValue: '0' },
        { key: 'due_date', label: 'Due date (YYYY-MM-DD)', type: 'text', defaultValue: '' },
        { key: 'paid', label: 'Paid?', type: 'select', defaultValue: 'Pending', options: ['Pending', 'Paid'] },
        { key: 'provider', label: 'Provider', type: 'text', defaultValue: '' },
        { key: 'notes', label: 'Notes', type: 'text', defaultValue: '' },
      ];
    case 'car_maintenance':
    case 'bike_maintenance':
      return [
        { key: 'date', label: 'Date (YYYY-MM-DD)', type: 'text', defaultValue: todayIso() },
        { key: 'item', label: 'Item / service', type: 'text', defaultValue: 'Service' },
        { key: 'amount', label: 'Amount (INR)', type: 'number', defaultValue: '0' },
        { key: 'notes', label: 'Notes', type: 'text', defaultValue: '' },
      ];
    case 'petrol':
      return [
        { key: 'date', label: 'Date (YYYY-MM-DD)', type: 'text', defaultValue: todayIso() },
        { key: 'vehicle', label: 'Vehicle', type: 'select', defaultValue: 'Car', options: ['Car', 'Bike'] },
        { key: 'litres', label: 'Litres', type: 'number', defaultValue: '0' },
        { key: 'amount', label: 'Amount (INR)', type: 'number', defaultValue: '0' },
        { key: 'notes', label: 'Notes', type: 'text', defaultValue: '' },
      ];
    case 'insurance':
      return [
        { key: 'date', label: 'Date (YYYY-MM-DD)', type: 'text', defaultValue: todayIso() },
        { key: 'policy', label: 'Policy', type: 'text', defaultValue: 'Health / Car / Bike' },
        { key: 'amount', label: 'Premium (INR)', type: 'number', defaultValue: '0' },
        { key: 'paid_via', label: 'Paid via', type: 'text', defaultValue: 'UPI' },
        { key: 'notes', label: 'Notes', type: 'text', defaultValue: '' },
      ];
    case 'medical':
      return [
        { key: 'date', label: 'Date (YYYY-MM-DD)', type: 'text', defaultValue: todayIso() },
        { key: 'type', label: 'Type', type: 'text', defaultValue: 'Pharmacy / Clinic / Hospital' },
        { key: 'who', label: 'Who', type: 'text', defaultValue: 'Family' },
        { key: 'amount', label: 'Amount (INR)', type: 'number', defaultValue: '0' },
        { key: 'paid_via', label: 'Paid via', type: 'text', defaultValue: 'UPI' },
        { key: 'notes', label: 'Notes', type: 'text', defaultValue: '' },
      ];
    default:
      return [
        { key: 'date', label: 'Date (YYYY-MM-DD)', type: 'text', defaultValue: todayIso() },
        { key: 'item', label: 'Item', type: 'text', defaultValue: 'Groceries' },
        { key: 'amount', label: 'Amount (INR)', type: 'number', defaultValue: '0' },
        { key: 'notes', label: 'Notes', type: 'text', defaultValue: '' },
      ];
  }
}
