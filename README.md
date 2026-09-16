# chai thoughts

One line, every chai. Type what's on your mind at each chai break, and after a
few entries, get a one-sentence AI reflection on your recurring themes.

Everytime you sit down in your break to drink your Chai. write one scentence in
it. Than analyze your thoughts after weeks.

## Run it live (free)

The app runs as a small Flask server. The easiest free hosts are
[Render](https://render.com) or [Hugging Face Spaces](https://huggingface.co/spaces) —
push this repo, point the service at it, and add one environment variable:

```
GEMINI_API_KEY=your-key-from-aistudio.google.com/apikey
```

Render: build `pip install -r requirements.txt`, start `gunicorn app:app`.
Spaces: the included `Dockerfile` works as-is (it exposes port 7860).

Free tier note: some hosts sleep after 15 minutes of no visitors and take
~30-50 seconds to wake on the next visit. That's the only cost of "free."

## How memory works

Each visitor gets a private cookie the first time they open the site. Their
entries are saved under that cookie's ID, so closing and reopening the site
(same browser) shows their data again. Nobody sees anyone else's entries.

## Run it locally instead

```
pip install -r requirements.txt
```
Copy `.env.example` to `.env`, paste in your Gemini key.
```
python app.py
```

## Old desktop version

The `chai.bat` / `chai_review.bat` scripts are the original offline version —
double-click to log one line locally, or run a local review of your entries.
The hosted app in `app.py` is the new way to use it.
