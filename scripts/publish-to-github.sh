#!/bin/bash
# Create GitHub repo and push (requires: gh auth login)
set -euo pipefail

REPO_NAME="${1:-org-chat-kit}"
VISIBILITY="${2:-public}"

if ! gh auth status &>/dev/null; then
  echo "Not logged in. Run:"
  echo "  gh auth login"
  echo "Then re-run this script."
  exit 1
fi

cd "$(dirname "$0")/.."

if git remote get-url origin &>/dev/null; then
  echo "Remote already set. Pushing..."
  git push -u origin main
else
  gh repo create "yellaiahvemula/${REPO_NAME}" \
    --${VISIBILITY} \
    --description "Python-only RAG + agents kit for govt/MSME conversational AI" \
    --source=. \
    --remote=origin \
    --push
fi

echo ""
echo "Done! https://github.com/yellaiahvemula/${REPO_NAME}"
