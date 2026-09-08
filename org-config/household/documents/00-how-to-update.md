# How to Maintain Household Expense Documents

## Purpose
All household expense data lives as markdown under `org-config/household/documents/`.
The chat assistant answers **only** from these files after you ingest them into RAG.

## Files

| File | What to put here |
|------|------------------|
| `monthly-summary.md` | One-page totals for the current month |
| `home-loan.md` | EMI, outstanding, payment history |
| `credit-cards.md` | Cards + statement amounts |
| `utilities.md` | Gas + electricity |
| `vehicles.md` | Car/bike service + petrol |
| `insurance.md` | Premiums and due dates |
| `medical.md` | Pharmacy, clinic, hospitalisation |
| `daily-expenses.md` | Groceries and small daily spends |

## Everyday workflow (for now)
1. Edit the markdown file(s) with your real numbers (replace SAMPLE)
2. Re-ingest: `make ingest ORG=household`
3. Open chat UI and select **Home Budget Assistant**
4. Ask questions like "What is my home loan EMI?" or "Total spend in September?"

## Adding more data later
- Append new month sections (do not delete old months if you want history)
- Add new `.md` files for new categories (e.g. `school-fees.md`) — ingest picks them up automatically
- Future: a form UI can write these same files or a DB; chat can stay as-is

## Privacy
- Never store full card numbers, CVV, OTPs, or netbanking passwords
- Last 4 digits of cards is enough if needed
