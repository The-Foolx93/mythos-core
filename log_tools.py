def calc_prune_xp(removed_count):
    return min(35, 8 + removed_count * 3), max(1, min(6, 1 + removed_count // 4))


def print_log(state, limit=15, show_all=False):
    completed = state.get("completed_quests", [])
    history = state.get("history", [])
    print("\n=== [ COMPLETED QUESTS ] ===")
    q_slice = completed if show_all else completed[-limit:]
    for i, q in enumerate(q_slice, 1):
        print(f"  {i}. {q}")
    if not q_slice:
        print("  (none)")
    print("\n=== [ EXECUTION LOG ] ===")
    h_slice = history if show_all else history[-limit:]
    for entry in h_slice:
        print(f"  - {entry}")
    if not h_slice:
        print("  (empty)")
    print("==============================\n")
