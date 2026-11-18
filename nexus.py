
import json
import os
import sys
from datetime import datetime

STATE_FILE = "system_state.json"
CODEX_FILE = "CODEX.md"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {
        "player": "Alexander the Grey",
        "level": 1,
        "active_quest": "Configure Local Git Repository",
        "inventory": ["Python 3.13.5", "Bash Shell", "Markdown Codex", "Git v2.47.3"],
        "history": []
    }

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)
    export_codex(state)

def export_codex(state):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# MythOS Core — System Codex",
        f"*Last Synchronized: {now}*\n",
        f"## Operator Status",
        f"- **Identity:** {state['player']}",
        f"- **System Level:** {state['level']}",
        f"- **Active Quest:** {state['active_quest']}\n",
        f"## Acquired Modules & Inventory",
    ]
    for item in state["inventory"]:
        lines.append(f"- [x] {item}")
    
    lines.append("\n## Execution Log")
    for entry in state.get("history", [])[-10:]:
        lines.append(f"- `{entry}`")

    with open(CODEX_FILE, "w") as f:
        f.write("\n".join(lines) + "\n")

def print_status(state):
    print("\n=== [ ACTIVE SYSTEM STATE ] ===")
    print(json.dumps(state, indent=4))
    print("===============================\n")

if __name__ == "__main__":
    state = load_state()
    if "history" not in state:
        state["history"] = []

    if len(sys.argv) < 2:
        print_status(state)
        sys.exit(0)

    command = sys.argv[1].lower()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    if command == "status":
        print_status(state)

    elif command == "quest" and len(sys.argv) > 2:
        new_quest = " ".join(sys.argv[2:])
        state["active_quest"] = new_quest
        state["history"].append(f"[{timestamp}] QUEST SET: {new_quest}")
        save_state(state)
        print(f"[ QUEST UPDATED ]: {new_quest} -> CODEX.md synchronized.")

    elif command == "item" and len(sys.argv) > 2:
        new_item = " ".join(sys.argv[2:])
        state["inventory"].append(new_item)
        state["level"] += 1
        state["history"].append(f"[{timestamp}] ITEM ACQUIRED: {new_item} (Lvl {state['level']})")
        save_state(state)
        print(f"[ ITEM ACQUIRED ]: {new_item} (Level {state['level']}) -> CODEX.md synchronized.")

    else:
        print("Commands: status | quest <name> | item <name>")

