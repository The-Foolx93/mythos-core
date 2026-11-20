import curses

def _bar(xp, cap=100, width=20):
    filled = max(0, min(width, int((xp / max(1, cap)) * width)))
    return "[" + "#" * filled + "-" * (width - filled) + "]"

def run_tui(state):
    def _draw(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(False)
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        tab = 0
        scroll = 0
        tabs = ["[1] Status", "[2] Quests", "[3] Skills", "[4] Log"]
        while True:
            stdscr.erase()
            h, w = stdscr.getmaxyx()
            player = state.get("player") or "Alexander the Grey"
            lvl = state.get("level", 21)
            xp = state.get("xp", 0)
            quest = state.get("active_quest") or "None"
            skills = state.get("skills", {})
            hist = state.get("history", [])
            attr_hi = curses.color_pair(1) | curses.A_BOLD if curses.has_colors() else curses.A_BOLD
            attr_sub = curses.color_pair(2) if curses.has_colors() else curses.A_NORMAL
            title = f" MYTHOS // {player}  LV.{lvl} {_bar(xp)} {xp}/100 XP "[:max(1, w-1)]
            stdscr.addnstr(0, 0, title, max(1, w-1), attr_hi)
            nav = "  ".join(f"*{t}*" if i == tab else t for i, t in enumerate(tabs))
            stdscr.addnstr(2, 0, nav[:max(1, w-1)], max(1, w-1), attr_sub)
            stdscr.hline(3, 0, curses.ACS_HLINE, max(1, w-1))
            lines = []
            if tab == 0:
                lines = ["=== OPERATOR STATUS ===", f"Operator : {player}", f"Level    : {lvl}", f"XP       : {xp}/100 {_bar(xp)}", f"Quest    : {quest}", f"Skills   : {len(skills)} tracked", f"Log Count: {len(hist)} entries", "", "Use [1]-[4] or Left/Right to switch tabs. Press q to quit."]
            elif tab == 1:
                lines = ["=== ACTIVE QUEST ===", f"Current  : {quest}", "", "=== QUEST CONTROLS ===", "Switch to [1] Status for stats or [4] Log for history."]
            elif tab == 2:
                lines = ["=== SKILL & TIER DECK ==="]
                for k, v in skills.items():
                    if isinstance(v, dict):
                        lines.append(f"  {k}: {v.get('points', 0)} PT ({v.get('_tier', '-')})")
                    else:
                        lines.append(f"  {k}: {v}")
                if len(lines) == 1:
                    lines.append("  No skills recorded yet.")
            else:
                lines = ["=== SYSTEM LOG ==="] + [str(x) for x in reversed(hist)]
            body_h = max(1, h - 6)
            scroll = max(0, min(scroll, max(0, len(lines) - body_h)))
            for idx, line in enumerate(lines[scroll:scroll + body_h]):
                stdscr.addnstr(4 + idx, 0, line[:max(1, w-1)], max(1, w-1), attr_hi if idx == 0 else (curses.color_pair(1) if curses.has_colors() else 0))
            footer = " [1-4] Tab  [Left/Right] Switch  [j/k] Scroll  [q] Quit "[:max(1, w-1)]
            stdscr.addnstr(max(0, h-1), 0, footer, max(1, w-1), attr_sub)
            stdscr.refresh()
            try:
                ch = stdscr.getch()
            except KeyboardInterrupt:
                break
            if ch in (ord("q"), ord("Q"), 27):
                break
            elif ch in (ord("1"), ord("2"), ord("3"), ord("4")):
                tab = ch - ord("1")
            elif ch == curses.KEY_RIGHT:
                tab = (tab + 1) % len(tabs)
            elif ch == curses.KEY_LEFT:
                tab = (tab - 1) % len(tabs)
            elif ch in (ord("j"), curses.KEY_DOWN):
                scroll += 1
            elif ch in (ord("k"), curses.KEY_UP):
                scroll = max(0, scroll - 1)
    try:
        curses.wrapper(_draw)
    except KeyboardInterrupt:
        pass
