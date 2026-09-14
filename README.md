# chai check-in

Everytime you sit down in your break to drink your Chai. write one scentence in it. Than analyze your thoughts after weeks.

# How to?
Double-click `chai.bat` — a clean terminal opens, asks what's on your mind, you type one line, it saves, it closes.

Double-click `chai_review.bat` after a few weeks to see your entries grouped by theme, using sentence embeddings — so similar *meanings* cluster together, not just matching keywords.

**Setup:** requires Python installed. First `chai_review.bat` run needs:
```
pip install sentence-transformers scikit-learn transformers torch
```
First review also downloads a small local model (~1GB, one-time) to write the natural language summaries.

**Data:** stored locally in `chai_log.jsonl`, next to the scripts. 
