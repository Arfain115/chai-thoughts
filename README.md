# chai check-in

One sentence, every chai. No app, no reminders, no typing commands.

Double-click `chai.bat` — a clean terminal opens, asks what's on your mind, you type one line, it saves, it closes. Do that daily.

Double-click `chai_review.bat` after a few weeks to see your entries grouped by theme, using sentence embeddings — so similar *meanings* cluster together, not just matching keywords.

**Setup:** requires Python installed. First `chai_review.bat` run needs:
```
pip install sentence-transformers scikit-learn transformers torch
```
First review also downloads a small local model (~1GB, one-time) to write the "hmm, seems like..." summaries.

**Data:** stored locally in `chai_log.jsonl`, next to the scripts. Never uploaded anywhere. Ignored by git on purpose — it's yours, not the repo's.
"# chai-thoughts" 
