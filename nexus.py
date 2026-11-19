import json
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "system_state.json")
CODEX_FILE = os.path.join(BASE_DIR, "CODEX.md")

XP_PER_LEVEL = 100


def load_state():
    default_state = {
        "player": "Alexander the Grey",
        "level": 3,
        "xp": 0,
        "active_quest": "Automate Local Knowledge Pipeline",
        "completed_quests": [],
        "skills": {
            "Python": 10,
            "Linux/CLI": 10,
            "Git": 5
        },
        "inventory": ["Python 3.13.5", "Bash Shell", "Markdown Codex", "Git v2.47.3"],
        "history": []
    }

    if not os.path.exists(STATE_FILE):
        return default_state

    with open(STATE_FILE, "r") as f:
        state = json.load(f)

    # Backfill new fields cleanly for older state files
    for key, value in default_state.items():
        if key not in state:
            state[key] = value.copy() if isinstance(value, (list, dict)) else value

    return state


def award_xp(state, amount, skill_name=None, skill_gain=5):
    state["xp"] += amount
    while state["xp"] >= XP_PER_LEVEL:
        state["xp"] -= XP_PER_LEVEL
        state["level"] += 1

    if skill_name:
        current_skill = state["skills"].get(skill_name, 0)
        state["skills"][skill_name] = current_skill + skill_gain


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)
    export_codex(state)


def export_codex(state):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# MythOS Core — System Codex",
        f"*Last Synchronized: {now}*\n",
        "## Operator Status",
        f"- **Identity:** {state['player']}",
        f"- **System Level:** {state['level']}",
        f"- **XP Progress:** {state['xp']} / {XP_PER_LEVEL} XP to next level",
        f"- **Active Quest:** {state['active_quest']}\n",
        "## Skills",
    ]

    if state["skills"]:
        for skill, rank in sorted(state["skills"].items(), key=lambda x: (-x[1], x[0])):
            lines.append(f"- **{skill}:** Rank {rank}")
    else:
        lines.append("- *No skills recorded yet.*")

    lines.append("\n## Completed Quests")
    if state["completed_quests"]:
        for q in state["completed_quests"][-10:]:
            lines.append(f"- [x] {q}")
    else:
        lines.append("- *None completed yet.*")

    lines.append("\n## Acquired Modules & Inventory")
    for item in state["inventory"]:
        lines.append(f"- [x] {item}")

    lines.append("\n## Execution Log")
    for entry in state.get("history", [])[-15:]:
        lines.append(f"- `{entry}`")

    with open(CODEX_FILE, "w") as f:
        f.write("\n".join(lines) + "\n")


def print_status(state):
    print("\n=== [ ACTIVE SYSTEM STATE ] ===")
    print(json.dumps(state, indent=4))
    print("===============================\n")


def print_usage():
    print("Usage:")
    print("  mythos status")
    print('  mythos quest "<new_quest>"')
    print('  mythos complete [optional_skill_name]')
    print('  mythos item "<new_item>" [optional_skill_name]')
    print('  mythos skill "<skill_name>" [amount]')


if __name__ == "__main__":
    state = load_state()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    if len(sys.argv) < 2:
        print_status(state)
        print_usage()
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "status":
        print_status(state)

    elif command == "quest" and len(sys.argv) > 2:
        new_quest = " ".join(sys.argv[2:])
        state["active_quest"] = new_quest
        state["history"].append(f"[{timestamp}] QUEST SET: {new_quest}")
        save_state(state)
        print(f"[ QUEST UPDATED ]: {new_quest} -> CODEX.md synchronized.")

    elif command == "complete":
        finished = state.get("active_quest")
        if not finished or finished == "None":
            print("No active quest to complete. Set one first with: mythos quest \"...\"")
            sys.exit(1)

        skill_arg = sys.argv[2] if len(sys.argv) > 2 else "Linux/CLI"
        xp_reward = 50
        state["completed_quests"].append(f"{finished} ({timestamp})")
        award_xp(state, xp_reward, skill_name=skill_arg, skill_gain=10)
        state["active_quest"] = "None"
        state["history"].append(
            f"[{timestamp}] QUEST COMPLETED: {finished} (+{xp_reward} XP, +10 {skill_arg})"
        )
        save_state(state)
        print(
            f"[ QUEST COMPLETE ]: {finished} | +{xp_reward} XP | +10 {skill_arg} "
            f"(Lvl {state['level']}, {state['xp']}/{XP_PER_LEVEL} XP)"
        )

    elif command == "item" and len(sys.argv) > 2:
        # Optional last arg if user passes a skill tag like: mythos item "Parser" Python
        skill_arg = "Python"
        item_parts = sys.argv[2:]
        if len(item_parts) >= 2 and item_parts[-1] in state["skills"]:
            skill_arg = item_parts[-1]
            item_parts = item_parts[:-1]

        new_item = " ".join(item_parts)
        state["inventory"].append(new_item)
        award_xp(state, 35, skill_name=skill_arg, skill_gain=5)
        state["history"].append(
            f"[{timestamp}] ITEM ACQUIRED: {new_item} (+35 XP, +5 {skill_arg})"
        )
        save_state(state)
        print(
            f"[ ITEM ACQUIRED ]: {new_item} | +35 XP | +5 {skill_arg} "
            f"(Lvl {state['level']}, {state['xp']}/{XP_PER_LEVEL} XP)"
        )

    elif command == "skill" and len(sys.argv) > 2:
        amount = 10
        if len(sys.argv) > 3 and sys.argv[3].isdigit():
            skill_name = " ".join(sys.argv[2:-1])
            amount = int(sys.argv[-1])
        else:
            skill_name = " ".join(sys.argv[2:])

        award_xp(state, amount * 2, skill_name=skill_name, skill_gain=amount)
        state["history"].append(
            f"[{timestamp}] SKILL TRAINED: {skill_name} +{amount} (+{amount * 2} XP)"
        )
        save_state(state)
        print(
            f"[ SKILL UPDATED ]: {skill_name} -> Rank {state['skills'][skill_name]} "
            f"(Lvl {state['level']}, {state['xp']}/{XP_PER_LEVEL} XP)"
        )

    else:
        print("Unknown command or missing arguments.")
        print_usage()
