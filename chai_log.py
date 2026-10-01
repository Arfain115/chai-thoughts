import json
import os
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(HERE, "chai_log.jsonl")

os.system("cls" if os.name == "nt" else "clear")
print()
thought = input("  chai's ready. one sentence:\n\n  > ").strip()

if thought:
    entry = {"timestamp": datetime.now().isoformat(timespec="seconds"), "text": thought}
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("\n  saved.\n")
else:
    print("\n  (empty, nothing saved)\n")

input("  press enter to close...")
