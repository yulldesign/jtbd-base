#!/usr/bin/env python3
"""Helper for the local (Markdown vault) backend of the JTBD knowledge base.

Usage (from the user's project, or with --root):
  python3 jtbd_local.py index [--project P] [--kind KIND]
  python3 jtbd_local.py tree  [--project P]
  python3 jtbd_local.py next-id PREFIX        (JP, JOB, OUT, ALT, EV)
  python3 jtbd_local.py lint  [--project P] [--no-grammar]
  python3 jtbd_local.py graph [--project P]  (writes <vault>/Graph/index.md)
Options:
  --root PATH   project folder holding jtbd.config.yaml and the vault
                (default: $CLAUDE_PROJECT_DIR if set, else the current directory)
  --vault PATH  overrides vault_path from jtbd.config.yaml
Requires Python 3.8+.
Standard library only.
"""
import argparse, datetime, json, os, re, sys
from pathlib import Path

KINDS = {"performers": "JP", "jobs": "JOB", "outcomes": "OUT", "alternatives": "ALT", "evidence": "EV"}
PREFIX_TO_KIND = {v: k for k, v in KINDS.items()}
STATUS = {"Hypothesis", "Supported", "Validated", "Deprecated"}
JOB_TYPES = {"Main job", "Job step", "Sub-job", "Emotional job", "Social job", "Related job"}
LINK = re.compile(r"\[\[([A-Z]+-\d+)(?:\|[^\]]*)?\]\]")


def config(root):
    cfg = {"vault_path": "jtbd-base", "projects": []}
    md = root / "jtbd.config.yaml"
    if md.exists():
        text = md.read_text(encoding="utf-8")
        m = re.search(r"^vault_path:\s*([^\s#]+)", text, re.M)
        if m:
            cfg["vault_path"] = m.group(1)
        m = re.search(r"^projects:\s*\[(.*?)\]", text, re.M)
        if m:
            cfg["projects"] = [p.strip().strip("\"'") for p in m.group(1).split(",") if p.strip()]
    return cfg


def parse_value(raw):
    raw = raw.strip()
    if raw == "" or raw in ("null", "~", '""', "''"):
        return None
    if raw.startswith("["):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return [x.strip().strip("\"'") for x in raw.strip("[]").split(",") if x.strip()]
    if raw[0] in "\"'":
        try:
            return json.loads(raw) if raw[0] == '"' else raw.strip("'")
        except json.JSONDecodeError:
            return raw.strip("\"'")
    try:
        return float(raw) if "." in raw else int(raw)
    except ValueError:
        return raw


def parse_file(path):
    text = path.read_text(encoding="utf-8")
    fm, body = {}, text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            block, body = text[3:end], text[end + 4:]
            key = None
            for line in block.splitlines():
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                if line.startswith(("  - ", "- ")) and key:
                    fm.setdefault(key, [])
                    if not isinstance(fm[key], list):
                        fm[key] = []
                    fm[key].append(parse_value(line.split("- ", 1)[1]))
                    continue
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    fm[key] = parse_value(val.split(" #")[0] if not val.strip().startswith(("\"", "'", "[")) else val)
    fm["_path"] = path
    fm["_body"] = body
    return fm


def links(value):
    if value is None:
        return []
    items = value if isinstance(value, list) else [value]
    out = []
    for it in items:
        out += LINK.findall(str(it))
    return out


def load(vault):
    data = {k: {} for k in KINDS}
    for kind in KINDS:
        folder = vault / kind
        if not folder.is_dir():
            continue
        for f in sorted(folder.glob("*.md")):
            e = parse_file(f)
            e["_kind"] = kind
            eid = e.get("id") or f.stem
            data[kind][str(eid)] = e
    return data


def by_id(data):
    return {i: e for kind in data.values() for i, e in kind.items()}


def label(e):
    return e.get("statement") or e.get("name") or e.get("title") or ""


def scores(e):
    i, s, p = e.get("importance"), e.get("satisfaction"), e.get("satisfaction_post")
    opp = quad = delta = None
    if isinstance(i, (int, float)) and isinstance(s, (int, float)):
        opp = round(i + max(i - s, 0), 1)
        quad = "Not worth going after" if i < 4 else ("Opportunity" if s < 4 else "Competitive market")
    if isinstance(p, (int, float)) and isinstance(s, (int, float)):
        delta = round(p - s, 1)
    return opp, quad, delta


# Statement grammar (heuristics, English). Findings are suggestions to review, not hard errors.
FORCES = ("Push", "Pull", "Anxiety", "Habit")
FUNCTIONAL = {"Main job", "Job step", "Sub-job", "Related job"}
NOT_A_VERB_START = {"the", "a", "an", "my", "our", "their", "his", "her", "its", "i", "we", "they", "you",
                    "to", "how", "when", "if", "while", "user", "users", "ability", "being", "be"}
QUALITY = re.compile(r"\b(quickly|easily|efficiently|effectively|effortlessly|seamless(?:ly)?|better|faster|easier|"
                     r"simpl[ey]|intuitive(?:ly)?|properly|best|smart(?:ly)?|optimal(?:ly)?)\b", re.I)
SOLUTION = re.compile(r"\b(using|via|tool|tools|app|apps|software|platform|dashboard|plugin|ai|chatbot)\b", re.I)
METRIC_WORDS = {
    "Time": r"\btime\b|\bhow long\b|\bduration\b",
    "Likelihood": r"\blikelihood\b|\bchance\b|\bprobability\b",
    "Effort": r"\beffort\b",
    "Number": r"\bnumber\b|\bamount\b|\bcount\b",
    "Cost": r"\bcost\b|\bexpense\b",
    "Risk": r"\brisk\b",
}
ANY_METRIC = re.compile("|".join(METRIC_WORDS.values()), re.I)


def section(body, name):
    m = re.search(rf"^##\s+{name}\s*$(.*?)(?=^##\s|\Z)", body or "", re.M | re.S | re.I)
    text = m.group(1).strip() if m else ""
    return "" if text in ("...", "…") else text


def forces_of(e):
    return {f: section(e.get("_body"), f) for f in FORCES}


def grammar(kind, e):
    """Return [(level, message)] for one entry."""
    out = []
    if e.get("status") == "Deprecated":
        return out
    text = str(label(e) or "").strip()
    words = text.split()
    first = words[0].lower().strip("\"'") if words else ""

    def common_checks(what):
        q = QUALITY.findall(text)
        if q:
            out.append(("low", f"{what} contains a quality word ({', '.join(sorted(set(w.lower() for w in q)))}): state the need, not how well"))
        s = SOLUTION.findall(text)
        if s:
            out.append(("low", f"{what} may name a solution ({', '.join(sorted(set(w.lower() for w in s)))}): keep it solution-free"))
        if text.endswith("?"):
            out.append(("low", f"{what} is a question, write it as a statement"))

    if kind == "jobs":
        t = e.get("type")
        if not text:
            out.append(("medium", "job without statement"))
        elif t == "Emotional job":
            if not re.match(r"(Feel|Avoid feeling)\b", text):
                out.append(("medium", 'emotional job should start with "Feel..." or "Avoid feeling..."'))
        elif t == "Social job":
            if not re.match(r"(Be perceived as|Avoid being perceived as|Be seen as|Avoid being seen as)\b", text):
                out.append(("medium", 'social job should start with "Be perceived as..." or "Avoid being perceived as..."'))
        elif t in FUNCTIONAL:
            if first in NOT_A_VERB_START:
                out.append(("low", f'job should start with an action verb, not "{words[0]}"'))
            elif first.endswith("ing") and len(first) > 5:
                out.append(("low", f'job starts with a gerund ("{words[0]}"): use the base verb'))
            if len(words) < 3:
                out.append(("low", "job statement too short: verb + object + context"))
            elif len(words) > 25:
                out.append(("low", "job statement very long: split it into steps or sub-jobs?"))
            common_checks("job")
    elif kind == "outcomes":
        if not text:
            out.append(("medium", "outcome without statement"))
            return out
        m = re.match(r"(Minimize|Increase)\b", text)
        direction = e.get("direction")
        if not m:
            out.append(("medium", 'outcome should start with "Minimize" or "Increase"'))
        elif direction in ("Minimize", "Increase") and m.group(1) != direction:
            out.append(("medium", f'direction is {direction} but the statement starts with "{m.group(1)}"'))
        metric = e.get("metric")
        if metric in METRIC_WORDS and not re.search(METRIC_WORDS[metric], text, re.I):
            out.append(("low", f"metric is {metric} but the statement does not mention it"))
        elif not ANY_METRIC.search(text):
            out.append(("low", "no metric in the statement (time, likelihood, effort, number, cost, risk)"))
        if len(words) < 6:
            out.append(("low", "outcome too short: direction + metric + object + context"))
        common_checks("outcome")
    elif kind == "alternatives":
        f = forces_of(e)
        if not any(f.values()):
            out.append(("low", "no forces documented (Push, Pull, Anxiety, Habit)"))
    elif kind == "evidence":
        force = e.get("force")
        if force and force not in FORCES:
            out.append(("medium", f"invalid force '{force}' (Push, Pull, Anxiety, Habit)"))
    return out


def evidence_index(data):
    idx = {}
    for ev_id, ev in data["evidence"].items():
        for field in ("performers", "jobs", "outcomes", "alternatives"):
            for target in links(ev.get(field)):
                idx.setdefault(target, []).append(ev)
    return idx


def in_project(e, project):
    return project is None or e.get("project") == project


def cmd_index(data, args):
    ev = evidence_index(data)
    kinds = [args.kind] if args.kind else list(KINDS)
    for kind in kinds:
        rows = [e for e in data[kind].values() if in_project(e, args.project)]
        if not rows:
            continue
        print(f"\n## {kind} ({len(rows)})\n")
        if kind in ("jobs", "outcomes"):
            print("| ID | Type | Statement | Parent | Status | Ev | I | S | Opp | Quadrant |")
            print("|---|---|---|---|---|---|---|---|---|---|")
            for i, e in sorted(data[kind].items(), key=lambda x: int(re.sub(r"\D", "", x[0]) or 0)):
                if not in_project(e, args.project):
                    continue
                parent = ",".join(links(e.get("parent") if kind == "jobs" else e.get("job")))
                opp, quad, _ = scores(e)
                typ = e.get("type") or (e.get("direction") or "")
                order = f" #{e['step_order']}" if e.get("step_order") is not None else ""
                print(f"| {i} | {typ}{order} | {label(e)} | {parent} | {e.get('status','')} | {len(ev.get(i, []))} | "
                      f"{e.get('importance') or ''} | {e.get('satisfaction') or ''} | {opp if opp is not None else ''} | {quad or ''} |")
        else:
            extra = kind == "alternatives"
            print("| ID | Name | Type | Links | Status | Ev |" + (" Forces |" if extra else ""))
            print("|---|---|---|---|---|---|" + ("---|" if extra else ""))
            for i, e in data[kind].items():
                if not in_project(e, args.project):
                    continue
                lk = ",".join(links(e.get("jobs")) + links(e.get("performers")) + links(e.get("outcomes")))
                typ = e.get("type", "") or ""
                if kind == "evidence" and e.get("force"):
                    typ = f"{typ} ({e['force']})"
                row = f"| {i} | {label(e)} | {typ} | {lk} | {e.get('status','') or ''} | {len(ev.get(i, []))} |"
                if extra:
                    f = forces_of(e)
                    row += " " + (" ".join(k for k in FORCES if f[k]) or "none") + " |"
                print(row)


def cmd_tree(data, args):
    jobs = data["jobs"]
    children = {}
    for i, j in jobs.items():
        for p in links(j.get("parent")):
            children.setdefault(p, []).append(i)
    outcomes = {}
    for i, o in data["outcomes"].items():
        for j in links(o.get("job")):
            outcomes.setdefault(j, []).append(i)

    def order(i):
        so = jobs[i].get("step_order")
        return (so if isinstance(so, (int, float)) else 999, i)

    def show(jid, depth):
        j = jobs[jid]
        print(f"{'  ' * depth}- {jid} [{j.get('type','?')}] {label(j)} ({j.get('status','')})")
        for o in outcomes.get(jid, []):
            oe = data["outcomes"][o]
            opp, quad, _ = scores(oe)
            extra = f", opp {opp}, {quad}" if opp is not None else ""
            print(f"{'  ' * (depth + 1)}* {o} {label(oe)} ({oe.get('status','')}{extra})")
        for c in sorted(children.get(jid, []), key=order):
            show(c, depth + 1)

    for pid, p in data["performers"].items():
        if not in_project(p, args.project):
            continue
        print(f"\n# {pid} {label(p)} ({p.get('status','')})")
        mains = [i for i, j in jobs.items() if pid in links(j.get("performer")) and not links(j.get("parent"))]
        for m in sorted(mains):
            show(m, 0)
    orphans = [i for i, j in jobs.items() if in_project(j, args.project) and not links(j.get("performer")) and not links(j.get("parent"))]
    if orphans:
        print("\n# Jobs without performer")
        for o in orphans:
            show(o, 0)


def cmd_graph(data, args, vault):
    """Write <vault>/Graph/index.md: one note linking every entry, as a hub for the Obsidian graph view."""
    jobs = data["jobs"]
    children, outcomes = {}, {}
    for i, j in jobs.items():
        for p in links(j.get("parent")):
            children.setdefault(p, []).append(i)
    for i, o in data["outcomes"].items():
        for j in links(o.get("job")):
            outcomes.setdefault(j, []).append(i)

    def wl(eid, e):
        text = re.sub(r"[\[\]|#^]", "", str(label(e))).strip()
        return f"[[{eid}|{eid} {text}]]" if text else f"[[{eid}]]"

    def order(i):
        so = jobs[i].get("step_order")
        return (so if isinstance(so, (int, float)) else 999, i)

    lines = []

    def show(jid, depth):
        j = jobs[jid]
        so = f" #{j['step_order']}" if j.get("step_order") is not None else ""
        lines.append(f"{'  ' * depth}- {wl(jid, j)} · {j.get('type', '?')}{so} · {j.get('status', '')}")
        for o in outcomes.get(jid, []):
            oe = data["outcomes"][o]
            lines.append(f"{'  ' * (depth + 1)}- {wl(o, oe)} · {oe.get('status', '')}")
        for c in sorted(children.get(jid, []), key=order):
            show(c, depth + 1)

    projects = sorted({str(e.get("project")) for kind in data.values() for e in kind.values()
                       if e.get("project") and in_project(e, args.project)})
    lines += ["---", "tags: [jtbd-graph]", "---", "# JTBD knowledge graph", "",
              f"Generated by `jtbd_local.py graph` on {datetime.date.today().isoformat()}. "
              "Do not edit by hand: the next run overwrites it.", "", "Writing rules: [[concepts]]"]
    for proj in projects:
        lines += ["", f"## {proj}"]
        for pid, p in data["performers"].items():
            if p.get("project") != proj:
                continue
            lines += ["", f"### {wl(pid, p)} · {p.get('status', '')}", ""]
            mains = [i for i, j in jobs.items() if pid in links(j.get("performer")) and not links(j.get("parent"))]
            for m in sorted(mains):
                show(m, 0)
        orphans = [i for i, j in jobs.items() if j.get("project") == proj
                   and not links(j.get("performer")) and not links(j.get("parent"))]
        if orphans:
            lines += ["", "### Jobs without performer", ""]
            for o in sorted(orphans):
                show(o, 0)
        for kind, field, title in (("alternatives", "jobs", "Alternatives"), ("evidence", None, "Evidence")):
            rows = [(i, e) for i, e in data[kind].items() if e.get("project") == proj]
            if not rows:
                continue
            lines += ["", f"### {title}", ""]
            for i, e in rows:
                targets = links(e.get(field)) if field else [t for f in ("performers", "jobs", "outcomes", "alternatives")
                                                             for t in links(e.get(f))]
                to = (" → " + ", ".join(f"[[{t}]]" for t in targets)) if targets else ""
                lines.append(f"- {wl(i, e)} · {e.get('type', '') or ''}{to}")
    out = vault / "Graph" / "index.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


def cmd_next_id(data, args):
    prefix = args.prefix.upper()
    if prefix not in PREFIX_TO_KIND:
        sys.exit(f"Unknown prefix {prefix}. Use one of {', '.join(PREFIX_TO_KIND)}")
    nums = [int(m.group(1)) for i in data[PREFIX_TO_KIND[prefix]] if (m := re.match(rf"{prefix}-(\d+)$", i))]
    print(f"{prefix}-{(max(nums) + 1 if nums else 1):03d}")


def cmd_lint(data, args, projects):
    ids = by_id(data)
    ev = evidence_index(data)
    issues = []

    def add(level, eid, msg):
        issues.append((level, eid, msg))

    seen = {}
    for kind, entries in data.items():
        for i, e in entries.items():
            if not in_project(e, args.project):
                continue
            if e["_path"].stem != i:
                add("medium", i, f"file name {e['_path'].name} does not match id")
            if not e.get("project"):
                add("medium", i, "missing project")
            elif projects and e.get("project") not in projects:
                add("low", i, f"project '{e.get('project')}' not listed in jtbd.config.yaml")
            if kind != "evidence":
                st = e.get("status")
                if st not in STATUS:
                    add("medium", i, f"invalid status '{st}'")
                n_ev = len(ev.get(i, []))
                if st in ("Supported", "Validated") and n_ev == 0:
                    add("high", i, f"{st} without linked evidence")
                if st == "Validated" and n_ev:
                    parts = {x.get("participant") for x in ev[i] if x.get("participant")}
                    survey = any(x.get("type") == "Survey" for x in ev[i])
                    if len(parts) < 3 and not survey:
                        add("medium", i, f"Validated with {len(parts)} participant(s) and no survey")
                key = (kind, str(label(e)).strip().lower())
                if key[1]:
                    if key in seen:
                        add("medium", i, f"same statement as {seen[key]}")
                    seen[key] = i
            for field, val in e.items():
                if field.startswith("_") or field == "aliases":
                    continue
                for target in links(val):
                    if target not in ids:
                        add("high", i, f"broken link [[{target}]] in '{field}'")
            for f in ("importance", "satisfaction", "satisfaction_post"):
                v = e.get(f)
                if v is not None and (not isinstance(v, (int, float)) or not 1 <= v <= 7):
                    add("medium", i, f"{f}={v} outside 1 to 7")
            if kind == "jobs":
                t = e.get("type")
                if t not in JOB_TYPES:
                    add("medium", i, f"invalid type '{t}'")
                if t in ("Job step", "Sub-job", "Emotional job", "Social job") and not links(e.get("parent")):
                    add("high", i, f"{t} without parent")
                if not links(e.get("performer")) and not links(e.get("parent")):
                    add("medium", i, "no performer and no parent")
                if t in ("Job step", "Sub-job") and e.get("step_order") is None:
                    add("low", i, "step without step_order")
            if kind == "outcomes":
                if not links(e.get("job")):
                    add("high", i, "outcome without job")
                if e.get("direction") not in ("Minimize", "Increase"):
                    add("medium", i, "missing or invalid direction")
                if e.get("satisfaction_post") is not None and e.get("satisfaction") is None:
                    add("low", i, "post-launch satisfaction without baseline")
            if kind == "alternatives" and not links(e.get("jobs")):
                add("medium", i, "alternative linked to no job")
            if not args.no_grammar:
                for lvl, msg in grammar(kind, e):
                    add(lvl, i, msg)
            if kind == "evidence":
                if not any(links(e.get(f)) for f in ("performers", "jobs", "outcomes", "alternatives")):
                    add("medium", i, "evidence linked to nothing")
                if re.search(r"[\w.+-]+@[\w-]+\.\w+", e["_body"]):
                    add("high", i, "quote seems to contain an email address")

    steps_with_outcomes = {t for o in data["outcomes"].values() for t in links(o.get("job"))}
    for i, j in data["jobs"].items():
        if in_project(j, args.project) and j.get("type") in ("Job step", "Sub-job") and i not in steps_with_outcomes:
            add("low", i, "step with no outcome")

    order = {"high": 0, "medium": 1, "low": 2}
    issues.sort(key=lambda x: (order[x[0]], x[1]))
    counts = {k: sum(1 for x in issues if x[0] == k) for k in order}
    total = {k: sum(1 for e in v.values() if in_project(e, args.project)) for k, v in data.items()}
    print(f"Entries: " + ", ".join(f"{k} {n}" for k, n in total.items()))
    print(f"Issues: {len(issues)} (high {counts['high']}, medium {counts['medium']}, low {counts['low']})")
    if issues:
        print("\n| Level | ID | Issue |\n|---|---|---|")
        for lvl, eid, msg in issues:
            print(f"| {lvl} | {eid} | {msg} |")
    return 1 if counts["high"] else 0


def main():
    ap = argparse.ArgumentParser(description="JTBD local vault helper")
    ap.add_argument("--root", help="project folder (default: $CLAUDE_PROJECT_DIR or the current directory)")
    ap.add_argument("--vault", help="vault folder (default: vault_path in jtbd.config.yaml)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("index"); p.add_argument("--project"); p.add_argument("--kind", choices=list(KINDS))
    p = sub.add_parser("tree"); p.add_argument("--project")
    p = sub.add_parser("next-id"); p.add_argument("prefix")
    p = sub.add_parser("lint"); p.add_argument("--project")
    p.add_argument("--no-grammar", action="store_true", help="skip statement grammar and forces checks")
    p = sub.add_parser("graph"); p.add_argument("--project")
    args = ap.parse_args()
    root = Path(args.root or os.environ.get("CLAUDE_PROJECT_DIR") or ".").resolve()
    cfg = config(root)
    vault = Path(args.vault) if args.vault else root / cfg["vault_path"]
    if not vault.is_dir():
        sys.exit(f"Vault folder not found: {vault}. Run /jtbd-base:setup with the local backend first, or pass --root.")
    data = load(vault)
    if args.cmd == "index":
        cmd_index(data, args)
    elif args.cmd == "tree":
        cmd_tree(data, args)
    elif args.cmd == "next-id":
        cmd_next_id(data, args)
    elif args.cmd == "lint":
        sys.exit(cmd_lint(data, args, cfg["projects"]))
    elif args.cmd == "graph":
        cmd_graph(data, args, vault)


if __name__ == "__main__":
    main()
