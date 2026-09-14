import json
import os
import traceback
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(HERE, "chai_log.jsonl")


def load_entries():
    if not os.path.exists(LOG_FILE):
        return []
    entries = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def when_was_it(timestamp_str):
    entry_time = datetime.fromisoformat(timestamp_str)
    days_ago = (datetime.now() - entry_time).days
    if days_ago == 0:
        return "today"
    if days_ago == 1:
        return "yesterday"
    return f"{days_ago} days ago"


def reflect_on_group(pipe, texts):
    """Ask the tiny LLM for one short, casual line summarizing the vibe of a group."""
    joined = "\n".join(f"- {t}" for t in texts)
    messages = [
        {
            "role": "system",
            "content": (
                "You reflect back patterns from someone's one-line daily journal entries. "
                "Given a few related entries, respond with exactly ONE short, casual sentence "
                "starting with 'hmm, seems like...' that captures the vibe. "
                "Do not list the entries back. Do not add extra commentary. One sentence only."
            ),
        },
        {"role": "user", "content": joined},
    ]
    prompt = pipe.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    output = pipe(
        prompt,
        max_new_tokens=40,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        pad_token_id=pipe.tokenizer.eos_token_id,
    )
    generated = output[0]["generated_text"][len(prompt):].strip()
    # keep just the first line/sentence, in case it rambles
    generated = generated.split("\n")[0].strip()
    if not generated.lower().startswith("hmm"):
        generated = "hmm, seems like... " + generated
    return generated


def main():
    os.system("cls" if os.name == "nt" else "clear")
    print()

    entries = load_entries()

    if len(entries) < 2:
        print(f"  only {len(entries)} entry logged so far.")
        print("  log at least one more before reviewing.\n")
        return

    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.cluster import AgglomerativeClustering
    except ImportError:
        print("  first time running review - needs a few packages installed.")
        print("  open cmd and run:\n")
        print("    pip install sentence-transformers scikit-learn transformers torch\n")
        return

    try:
        from transformers import pipeline
        llm_available = True
    except ImportError:
        llm_available = False

    print("  give me a second to read through what you've written...\n")

    texts = [e["text"] for e in entries]
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts)

    n_clusters = max(2, min(6, len(entries) // 3))
    n_clusters = min(n_clusters, len(entries))
    labels = AgglomerativeClustering(n_clusters=n_clusters).fit_predict(embeddings)

    groups = {}
    for label, entry in zip(labels, entries):
        groups.setdefault(label, []).append(entry)

    for group in groups.values():
        group.sort(key=lambda e: e["timestamp"])

    ordered = sorted(groups.items(), key=lambda kv: -len(kv[1]))

    llm_pipe = None
    if llm_available:
        print("  loading the little model (first run downloads it, ~1GB, be patient)...\n")
        llm_pipe = pipeline(
            "text-generation",
            model="Qwen/Qwen2.5-0.5B-Instruct",
            device_map="cpu",
        )

    print(f"  you've checked in {len(entries)} times, and it mostly groups into {len(ordered)} things:\n")

    for i, (label, group) in enumerate(ordered, 1):
        group_texts = [e["text"] for e in group]

        if llm_pipe is not None:
            try:
                reflection = reflect_on_group(llm_pipe, group_texts)
                print(f"  {i}. {reflection}")
            except Exception:
                print(f"  {i}. this came up {len(group)} time{'s' if len(group) != 1 else ''}:")
        else:
            print(f"  {i}. this came up {len(group)} time{'s' if len(group) != 1 else ''}:")

        for e in group[:5]:
            when = when_was_it(e["timestamp"])
            print(f"     - {when}: {e['text']}")
        if len(group) > 5:
            print(f"     ...and {len(group) - 5} more")
        print()

    if not llm_available:
        print("  (tip: run 'pip install transformers torch' for a friendlier one-line summary per theme)\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("\n  something went wrong:\n")
        traceback.print_exc()
    input("\n  press enter to close...")
