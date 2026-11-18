import json
import os
import sys

STATE_FILE = "system_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {
        "player": "Alexander the Grey",
        "level": 1,
        "active_quest": "Deploy Local Linux Stack",
        "inventory": ["Python 3.13.5", "Bash Shell", "Markdown Codex"]
    }

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def print_status(state):
    print("\n=== [ ACTIVE SYSTEM STATE ] ===")
    print(json.dumps(state, indent=4))
    print("===============================\n")

if __name__ == "__main__":
    state = load_state()

    # Simple command handling without external bloat
    if len(sys.argv) < 2:
        print_status(state)
        print("Usage: python3 nexus.py [status | quest <new_quest> | item <new_item>]")
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "status":
        print_status(state)

    elif command == "quest" and len(sys.argv) > 2:
        new_quest = " ".join(sys.argv[2:])
        state["active_quest"] = new_quest
        save_state(state)
        print(f"[ QUEST UPDATED ]: {new_quest}")

    elif command == "item" and len(sys.argv) > 2:
        new_item = " ".join(sys.argv[2:])
        state["inventory"].append(new_item)
        state["level"] += 1  # Gain a level for acquiring new assets
        save_state(state)
        print(f"[ ITEM ACQUIRED ]: {new_item} (Level Up! Current Level: {state['level']})")

    else:
        print("Unknown command or missing arguments.")
        print("Commands: status, quest [name], item [name]")
