import json
import os
import subprocess
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "system_state.json")
CODEX_FILE = os.path.join(BASE_DIR, "CODEX.md")
BUNDLE_FILE = os.path.join(BASE_DIR, "NOTEBOOK_BUNDLE.md")
XP_PER_LEVEL = 100


def default_state():
    return {
        "player": "Alexander the Grey",
        "level": 3,
        "xp": 50,
        "active_quest": "Establish GitHub Remote Sync",
        "completed_quests": ["Automate Local Knowledge Pipeline (2026-11-18 16:31)"],
        "skills": {
            "Python": 20,
            "Linux/CLI": 10,
            "Git": 5,
        },
        "inventory": [
            "Python 3.13.5",
            "Bash Shell",
            "Markdown Codex",
            "Global Shell Alias",
            "Git v2.47.3",
        ],
        "history": [],
    }


def load_state():
    base = default_state()
    if not os.path.exists(STATE_FILE):
        return base
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    for key, val in base.items():
        if key not in loaded:
            loaded[key] = val.copy() if isinstance(val, (list, dict)) else val
    return loaded


def apply_xp(state, xp_gain, skill_name=None, skill_gain=0):
    xp_gain = max(1, int(round(xp_gain)))
    state["xp"] += xp_gain
    leveled_up = 0
    while state["xp"] >= XP_PER_LEVEL:
        state["xp"] -= XP_PER_LEVEL
        state["level"] += 1
        leveled_up += 1

    actual_skill_gain = 0
    if skill_name and skill_gain > 0:
        actual_skill_gain = max(1, int(round(skill_gain)))
        state["skills"][skill_name] = state["skills"].get(skill_name, 0) + actual_skill_gain

    return xp_gain, actual_skill_gain, leveled_up


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
        for skill, rank in sorted(state["skills"].items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"- **{skill}:** Rank {rank}")
    else:
        lines.append("- *No skills recorded yet.*")

    lines.append("\n## Completed Quests")
    if state["completed_quests"]:
        for quest in state["completed_quests"][-10:]:
            lines.append(f"- [x] {quest}")
    else:
        lines.append("- *None completed yet.*")

    lines.append("\n## Acquired Modules & Inventory")
    for item in state["inventory"]:
        lines.append(f"- [x] {item}")

    lines.append("\n## Execution Log")
    for entry in state.get("history", [])[-15:]:
        lines.append(f"- `{entry}`")

    with open(CODEX_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)
    export_codex(state)


def calc_commit_xp(cwd):
    res = subprocess.run(
        ["git", "diff", "--cached", "--numstat"],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    files_changed = 0
    lines_delta = 0
    for line in res.stdout.strip().splitlines():
        parts = line.split("\t")
        if len(parts) >= 3:
            files_changed += 1
            added = int(parts[0]) if parts[0].isdigit() else 0
            deleted = int(parts[1]) if parts[1].isdigit() else 0
            lines_delta += added + deleted

    # Base 15 XP + line delta scaling (capped) + multi-file bonus
    xp = 15 + min(45, lines_delta // 3) + max(0, (files_changed - 1) * 5)
    skill_gain = max(2, min(12, 2 + lines_delta // 25 + files_changed))
    return xp, skill_gain, files_changed, lines_delta


def calc_quest_xp(quest_title):
    words = max(1, len(quest_title.split()))
    xp = 30 + min(40, words * 4)
    skill_gain = max(5, min(15, 5 + words))
    return xp, skill_gain


def calc_item_xp(item_name, inventory_len):
    words = max(1, len(item_name.split()))
    xp = 20 + min(30, words * 4) + min(15, inventory_len)
    skill_gain = max(3, min(10, 3 + words // 2))
    return xp, skill_gain


def calc_bundle_xp():
    total_lines = 0
    present_files = 0
    for path in (CODEX_FILE, STATE_FILE, os.path.join(BASE_DIR, "nexus.py")):
        if os.path.exists(path):
            present_files += 1
            with open(path, "r", encoding="utf-8") as f:
                total_lines += sum(1 for _ in f)
    xp = 15 + present_files * 5 + min(35, total_lines // 20)
    skill_gain = max(2, min(8, 2 + total_lines // 80))
    return xp, skill_gain, total_lines


def print_status(state):
    print("\n=== [ ACTIVE SYSTEM STATE ] ===")
    print(json.dumps(state, indent=4))
    print("===============================\n")


def print_usage():
    print("Usage:")
    print("  mythos status")
    print('  mythos quest "<new_quest>"')
    print("  mythos complete [skill_name]")
    print('  mythos item "<new_item>" [skill_name]')
    print('  mythos skill "<skill_name>" [amount]')
    print('  mythos commit "<commit_message>"')
    print("  mythos bundle")


def main():
    state = load_state()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    if len(sys.argv) < 2:
        print_status(state)
        print_usage()
        return

    cmd = sys.argv[1].lower()

    if cmd == "status":
        print_status(state)

    elif cmd == "quest" and len(sys.argv) > 2:
        new_quest = " ".join(sys.argv[2:]).strip()
        state["active_quest"] = new_quest
        state["history"].append(f"[{timestamp}] QUEST SET: {new_quest}")
        save_state(state)
        print(f"[ QUEST UPDATED ]: {new_quest}")

    elif cmd == "complete":
        active = state.get("active_quest")
        if not active or active == "None":
            print("No active quest to complete.")
            sys.exit(1)
        skill = sys.argv[2] if len(sys.argv) > 2 else "Linux/CLI"
        raw_xp, raw_skill = calc_quest_xp(active)
        xp_gained, sk_gained, lvls = apply_xp(state, raw_xp, skill, raw_skill)
        state["completed_quests"].append(f"{active} ({timestamp})")
        state["active_quest"] = "None"
        state["history"].append(
            f"[{timestamp}] QUEST COMPLETED: {active} (+{xp_gained} XP, +{sk_gained} {skill})"
        )
        save_state(state)
        lvl_note = f" | LEVEL UP -> {state['level']}" if lvls else ""
        print(
            f"[ QUEST COMPLETE ]: {active} | +{xp_gained} XP | +{sk_gained} {skill} "
            f"(Lvl {state['level']}, {state['xp']}/{XP_PER_LEVEL} XP){lvl_note}"
        )

    elif cmd == "item" and len(sys.argv) > 2:
        skill = "Python"
        parts = sys.argv[2:]
        if len(parts) >= 2 and parts[-1] in state["skills"]:
            skill = parts[-1]
            parts = parts[:-1]
        item_name = " ".join(parts).strip()
        raw_xp, raw_skill = calc_item_xp(item_name, len(state["inventory"]))
        xp_gained, sk_gained, lvls = apply_xp(state, raw_xp, skill, raw_skill)
        state["inventory"].append(item_name)
        state["history"].append(
            f"[{timestamp}] ITEM ACQUIRED: {item_name} (+{xp_gained} XP, +{sk_gained} {skill})"
        )
        save_state(state)
        lvl_note = f" | LEVEL UP -> {state['level']}" if lvls else ""
        print(
            f"[ ITEM ACQUIRED ]: {item_name} | +{xp_gained} XP | +{sk_gained} {skill} "
            f"(Lvl {state['level']}, {state['xp']}/{XP_PER_LEVEL} XP){lvl_note}"
        )

    elif cmd == "skill" and len(sys.argv) > 2:
        amount = 10
        if len(sys.argv) > 3 and sys.argv[3].isdigit():
            skill = " ".join(sys.argv[2:-1]).strip()
            amount = int(sys.argv[-1])
        else:
            skill = " ".join(sys.argv[2:]).strip()
        current_rank = state["skills"].get(skill, 0)
        # Diminishing returns at higher ranks, floor of 1 XP per point
        scaled_xp = max(amount, int(round(amount * (2.5 - min(1.5, current_rank * 0.05)))))
        xp_gained, sk_gained, lvls = apply_xp(state, scaled_xp, skill, amount)
        state["history"].append(
            f"[{timestamp}] SKILL TRAINED: {skill} +{sk_gained} (+{xp_gained} XP)"
        )
        save_state(state)
        lvl_note = f" | LEVEL UP -> {state['level']}" if lvls else ""
        print(
            f"[ SKILL UPDATED ]: {skill} Rank {state['skills'][skill]} | +{xp_gained} XP "
            f"(Lvl {state['level']}, {state['xp']}/{XP_PER_LEVEL} XP){lvl_note}"
        )

    elif cmd == "commit" and len(sys.argv) > 2:
        msg = " ".join(sys.argv[2:]).strip()
        stage = subprocess.run(["git", "add", "."], cwd=BASE_DIR)
        if stage.returncode != 0:
            print("[ ERROR ]: git add failed.")
            sys.exit(1)
        raw_xp, raw_skill, files_changed, lines_delta = calc_commit_xp(BASE_DIR)
        commit_res = subprocess.run(["git", "commit", "-m", msg], cwd=BASE_DIR)
        if commit_res.returncode == 0:
            xp_gained, sk_gained, lvls = apply_xp(state, raw_xp, "Git", raw_skill)
            state["history"].append(
                f"[{timestamp}] COMMIT: {msg} ({files_changed}f/{lines_delta}L, +{xp_gained} XP, +{sk_gained} Git)"
            )
            save_state(state)
            lvl_note = f" | LEVEL UP -> {state['level']}" if lvls else ""
            print(
                f"[ COMMITTED ]: {msg} | {files_changed} files, {lines_delta} lines delta | "
                f"+{xp_gained} XP | +{sk_gained} Git (Rank {state['skills']['Git']}){lvl_note}"
            )
        else:
            print("[ ERROR ]: git commit failed or nothing to commit.")

    elif cmd == "bundle":
        raw_xp, raw_skill, total_lines = calc_bundle_xp()
        parts = [
            "# MythOS Core — NotebookLM Source Bundle",
            f"*Generated: {timestamp}*",
            f"*Operator: {state['player']} | Level: {state['level']}*\n",
        ]
        for label, path, fence in (
            ("1. System Codex (CODEX.md)", CODEX_FILE, ""),
            ("2. System State JSON", STATE_FILE, "json"),
            ("3. Engine Source Code (nexus.py)", os.path.join(BASE_DIR, "nexus.py"), "python"),
        ):
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                parts.append(f"## {label}\n")
                if fence:
                    parts.append(f"```{fence}\n{content}\n```\n")
                else:
                    parts.append(f"{content}\n")
                parts.append("---\n")

        with open(BUNDLE_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(parts))

        xp_gained, sk_gained, lvls = apply_xp(state, raw_xp, "Python", raw_skill)
        state["history"].append(
            f"[{timestamp}] BUNDLE: NOTEBOOK_BUNDLE.md ({total_lines} lines scanned, +{xp_gained} XP, +{sk_gained} Python)"
        )
        save_state(state)
        lvl_note = f" | LEVEL UP -> {state['level']}" if lvls else ""
        print(
            f"[ BUNDLE CREATED ]: NOTEBOOK_BUNDLE.md ({total_lines} lines) | "
            f"+{xp_gained} XP | +{sk_gained} Python{lvl_note}"
        )

    else:
        print("Unknown command or missing arguments.")
        print_usage()


if __name__ == "__main__":
    main()
