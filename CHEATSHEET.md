# Cheat sheet

Everything you copy during the session lives on this page, in the order you need it. Each block says **what it does**, **what you should see**, and **what to do if you do not**.

The plan: you write a small script, `visibility.py`, in five steps. Each step adds one command to it, and you run that command right away, so you always know which step broke.

| Step | You add | You run | You get |
|---|---|---|---|
| M1 | the script skeleton | `python3 visibility.py plan` | the list of jobs, nothing is sent yet |
| M2 | the starter | `python3 visibility.py start` | jobs running on Bright Data's side |
| M3 | the collector | `python3 visibility.py collect` | one file per answer in `raw/` |
| M4 | the analyser | `python3 visibility.py report` | a summary in your terminal |
| M5 | the page builder | `python3 visibility.py html` | `report.html` in your browser |

Stuck at any point? Jump to [Troubleshooting](#troubleshooting). Want to see the finish line first? Open `building-blocks/sample-report.html` in your browser.

---

## 0. Setup commands

Run these once, in a terminal, inside the repo folder (`cd` into it first).

| Command | What it does | You should see |
|---|---|---|
| `node --version` | checks Node.js | `v20` or higher. If lower or missing, install Node.js 20+ |
| `python3 --version` | checks Python | `Python 3.9` or higher |
| `npm install -g @brightdata/cli` | installs the Bright Data CLI (`bdata`) | a few lines of npm output, no red errors |
| `bdata login` | opens your browser to sign in | "Logged in" or similar. On a remote machine use `bdata login --device` |
| `bdata pipelines search chatgpt` | proves you are logged in and can see scrapers | a JSON list that contains `ChatGPT Search` |

Co-pilot users also run `npx skills add brightdata/skills -g` once.

If `bdata pipelines search chatgpt` prints an error instead of a list, you are not logged in. Run `bdata login` again.

---

## 1. Fill in `config.json`

`config.json` is your one input file. It is already in the repo with placeholder values: open it in your editor and replace them. Everything the script does is driven by it.

```json
{
  "company": "Your Company",
  "domain": "yourcompany.com",
  "names": ["Your Company", "YourCo"],
  "competitors": ["Competitor One", "Competitor Two", "Competitor Three"],
  "prompts": [
    "What is Your Company known for, and who are its main competitors?",
    "What are the best <your category> for <your customer type>?"
  ],
  "engines": [
    {"name": "chatgpt", "dataset_id": "gd_m7aof0k82r803d5bjm", "url": "https://chatgpt.com/"},
    {"name": "gemini", "dataset_id": "gd_mbz66arm2mf9cu856y", "url": "https://gemini.google.com/"}
  ]
}
```

| Key | What to put there | Example |
|---|---|---|
| `company` | your company name as you would say it | `"Wonderful AI"` |
| `domain` | your website, without `https://` or `www.` | `"wonderful.ai"` |
| `names` | every way your company is written in text, longest first. Matching is case-sensitive | `["Wonderful AI", "Wonderful"]` |
| `competitors` | 3 to 10 companies you want counted in the answers | `["Sierra", "Decagon"]` |
| `prompts` | 2 or 3 questions. Choose from `building-blocks/prompts.md` or write your own | see that file |
| `engines` | the engines to ask. Copy the lines from `building-blocks/engines.md` | see that file |

**Choosing engines:** open <https://brightdata.com/cp/scrapers/browse?category=all>, find the AI scrapers you care about, and copy their lines from `building-blocks/engines.md`. Take two or three. More engines mean longer waiting and higher cost.

**Choosing Bing Copilot:** it starts through the REST API and needs an API key. Create one in your Bright Data account settings, then run `export BRIGHTDATA_API_KEY="your-key"` in the terminal you will use for step M2. Never paste the key into a file or a chat.

JSON rules that trip people up: double quotes only, a comma between entries, **no comma after the last entry**.

---

## M1. The script skeleton

Create an empty file called `visibility.py` in the repo folder and paste this whole block into it.

```python
#!/usr/bin/env python3
"""AI visibility check: asks AI engines about your company and builds a report."""
import html
import json
import os
import re
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.parse import urlparse


def load_config(folder="."):
    """Read config.json (from the folder if it has one, otherwise from here)."""
    path = Path(folder) / "config.json"
    if not path.exists():
        path = Path("config.json")
    try:
        cfg = json.loads(path.read_text())
    except Exception as e:
        sys.exit(f"Cannot read {path}: {e}")
    for key in ("company", "domain", "names", "competitors", "prompts", "engines"):
        if not cfg.get(key):
            sys.exit(f"config.json: '{key}' is missing or empty")
    for eng in cfg["engines"]:
        for key in ("name", "dataset_id", "url"):
            if not eng.get(key):
                sys.exit(f"config.json: an engine is missing '{key}': {eng}")
    return cfg


def jobs_from(cfg):
    """One job per (prompt, engine) pair, for example ('p1', prompt, engine)."""
    return [(f"p{i}", prompt, eng)
            for i, prompt in enumerate(cfg["prompts"], 1)
            for eng in cfg["engines"]]


def cmd_plan(arg=None):
    """Show what will run. Costs nothing."""
    cfg = load_config()
    jobs = jobs_from(cfg)
    print(f"Company: {cfg['company']} ({cfg['domain']})")
    print(f"{len(cfg['prompts'])} prompts x {len(cfg['engines'])} engines = {len(jobs)} jobs\n")
    for pid, prompt, eng in jobs:
        how = "REST" if eng.get("trigger") == "rest" else "CLI"
        print(f"  {pid}  {eng['name']:<14} {how:<5} {prompt}")
    print("\nLooks right? Next: python3 visibility.py start")


# >>> paste the next snippet above this line <<<


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "plan"
    handler = globals().get("cmd_" + command)
    if handler is None:
        sys.exit("Unknown command. Try: plan, start, collect, report, html")
    handler(*sys.argv[2:])
```

Run it:

```bash
python3 visibility.py plan
```

You should see your company, the number of jobs (prompts x engines) and one line per job, then `Looks right? Next: python3 visibility.py start`. Nothing has been sent and nothing costs money yet.

| If you see | Do this |
|---|---|
| `config.json: 'domain' is missing or empty` | fill in that key in `config.json` |
| `Cannot read config.json: ...` | a JSON typo, usually a missing or extra comma. Paste the file into any JSON validator |

---

## M2. Start the jobs

Paste this block into `visibility.py`, **above** the line `# >>> paste the next snippet above this line <<<`. (Every new block goes above that line, so the `if __name__` part stays at the bottom.)

```python
def trigger_cli(eng, prompt):
    """Start one job through the Bright Data CLI. Returns the snapshot id."""
    try:
        out = subprocess.run(
            ["bdata", "pipelines", "run", eng["dataset_id"], "collect_by_url", eng["url"],
             "--prompt", prompt, "--async", "--json"],
            capture_output=True, text=True)
    except FileNotFoundError:
        raise RuntimeError("the 'bdata' command was not found: install the CLI (README, step 2)")
    try:
        return json.loads(out.stdout)["snapshot_id"]
    except Exception:
        raise RuntimeError(out.stderr.strip() or out.stdout.strip() or "no answer from bdata")


def trigger_rest(eng, prompt):
    """Start one job through the REST API (needs BRIGHTDATA_API_KEY). Returns the snapshot id."""
    key = os.environ.get("BRIGHTDATA_API_KEY")
    if not key:
        raise RuntimeError("BRIGHTDATA_API_KEY is not set (see README, step 6)")
    url = ("https://api.brightdata.com/datasets/v3/trigger"
           f"?dataset_id={eng['dataset_id']}&include_errors=true")
    body = json.dumps([{"url": eng["url"], "prompt": prompt}])
    out = subprocess.run(
        ["curl", "-s", "-X", "POST", url, "-H", f"Authorization: Bearer {key}",
         "-H", "Content-Type: application/json", "-d", body],
        capture_output=True, text=True)
    try:
        return json.loads(out.stdout)["snapshot_id"]
    except Exception:
        raise RuntimeError(out.stdout.strip()[:200] or "no answer from the API")


def cmd_start(arg=None):
    """Start every job in parallel. They run on Bright Data's side, not on your laptop."""
    cfg = load_config()
    Path("raw").mkdir(exist_ok=True)
    started = []
    for pid, prompt, eng in jobs_from(cfg):
        trigger = trigger_rest if eng.get("trigger") == "rest" else trigger_cli
        try:
            sid = trigger(eng, prompt)
            print(f"started  {pid}  {eng['name']:<14} {sid}")
        except Exception as e:
            sid = None
            print(f"FAILED   {pid}  {eng['name']:<14} {e}")
        started.append({"prompt_id": pid, "engine": eng["name"], "snapshot_id": sid})
    Path("raw/jobs.json").write_text(json.dumps(started, indent=2))
    if any(j["snapshot_id"] for j in started):
        print("\nJobs are running. Next: python3 visibility.py collect")
    else:
        print("\nNothing started. Fix the errors above and run start again.")
```

Run it:

```bash
python3 visibility.py start
```

You should see one `started` line per job, with an id starting `sd_`, then `Jobs are running. Next: python3 visibility.py collect`. Your laptop is not doing the work: Bright Data's scrapers are.

| If you see | Do this |
|---|---|
| `the 'bdata' command was not found` | step 0: install the CLI, then open a new terminal |
| `BRIGHTDATA_API_KEY is not set` | you chose Bing Copilot: run the `export` line from step 1, in this terminal. Or remove Bing from `config.json` |
| other `FAILED` text | run `bdata login` again; if one engine keeps failing, remove it from `config.json` and run `start` again |

Do not run `start` twice to "speed things up": every run starts, and bills, new jobs.

---

## M3. Collect the answers

Paste above the marker:

```python
def cmd_collect(arg=None):
    """Wait for the jobs and save each answer to raw/<prompt>.<engine>.json. Safe to re-run."""
    jobs = json.loads(Path("raw/jobs.json").read_text())
    pending = [j for j in jobs if j["snapshot_id"]
               and not Path(f"raw/{j['prompt_id']}.{j['engine']}.json").exists()]
    started, last = time.time(), ""
    while pending and time.time() - started < 1500:
        for j in list(pending):
            r = subprocess.run(["bdata", "pipelines", "status", j["snapshot_id"], "--json"],
                               capture_output=True, text=True)
            try:
                status = json.loads(r.stdout).get("status", "?")
            except Exception:
                status = "?"
            label = f"{j['prompt_id']}  {j['engine']}"
            if status == "ready":
                res = subprocess.run(["bdata", "pipelines", "results", j["snapshot_id"], "--json"],
                                     capture_output=True, text=True)
                Path(f"raw/{j['prompt_id']}.{j['engine']}.json").write_text(res.stdout)
                pending.remove(j)
                print(f"done     {label}  after {int(time.time() - started)}s")
            elif status in ("failed", "error", "canceled"):
                pending.remove(j)
                print(f"FAILED   {label}")
        if pending:
            line = f"waiting for {len(pending)}: " + ", ".join(
                f"{j['prompt_id']}/{j['engine']}" for j in pending)
            if line != last:
                print(line)
                last = line
            time.sleep(10)
    print("\nNext: python3 visibility.py report")
```

Run it:

```bash
python3 visibility.py collect
```

It checks every ten seconds and prints a `done` line when an answer arrives. The first answers usually arrive within one to three minutes; ChatGPT and Google AI Mode can take up to ten. **While you wait, continue with M4 in a second terminal using the sample data** (see below).

Close the terminal by accident? No problem: run `python3 visibility.py collect` again. It skips what it already saved.

Check what you got:

```bash
ls -la raw/
```

Each file should be larger than 0 bytes: `p1.chatgpt.json`, `p1.gemini.json`, and so on. A `FAILED` line means the engine could not answer; the report will show "no data" for it.

---

## M4. The analyser and the text report

Paste above the marker:

```python
def host(url):
    h = urlparse(url).netloc.lower()
    return h[4:] if h.startswith("www.") else h


def analyse(cfg, record):
    """Turn one raw answer into a few numbers."""
    text = record.get("answer_text") or ""
    names = sorted(cfg["names"], key=len, reverse=True)
    name_re = r"(?<!\w)(?:" + "|".join(re.escape(n) for n in names) + r")(?!\w)"
    domains = []
    for c in record.get("citations") or []:
        d = host(c.get("url", ""))
        if d and d not in domains:
            domains.append(d)
    rivals = {}
    for c in cfg["competitors"]:
        n = len(re.findall(r"(?<!\w)" + re.escape(c) + r"(?!\w)", text))
        if n:
            rivals[c] = n
    return {"text": text, "mentions": len(re.findall(name_re, text)), "domains": domains,
            "own_cited": any(cfg["domain"] in d for d in domains), "competitors": rivals}


def load_results(folder="raw"):
    """Read every raw file. Returns (config, {(prompt_id, engine_name): analysis or None})."""
    cfg = load_config(folder)
    results = {}
    for pid, _, eng in jobs_from(cfg):
        try:
            record = json.loads((Path(folder) / f"{pid}.{eng['name']}.json").read_text())[0]
            results[pid, eng["name"]] = analyse(cfg, record)
        except Exception:
            results[pid, eng["name"]] = None
    return cfg, results


def cmd_report(folder="raw"):
    """Print a text summary: one line per prompt and engine."""
    cfg, results = load_results(folder)
    print(f"\nWhat does AI say about {cfg['company']}?\n")
    print(f"{'Prompt':<7}{'Engine':<16}{'Mentions':<10}{'Own site':<10}{'Sources':<9}Top competitors")
    for (pid, eng), a in results.items():
        if a is None:
            print(f"{pid:<7}{eng:<16}no data")
            continue
        top = ", ".join(f"{k} x{v}" for k, v in sorted(a["competitors"].items(), key=lambda kv: -kv[1])[:3])
        print(f"{pid:<7}{eng:<16}{a['mentions']:<10}{'yes' if a['own_cited'] else 'no':<10}"
              f"{len(a['domains']):<9}{top}")
    print("\nWant it as a web page? Next: python3 visibility.py html")
```

Try it on the sample data first, so you do not need to wait for your own answers:

```bash
python3 visibility.py report building-blocks/sample
```

You should see a table with one line per prompt and engine: mentions of the company, whether the company's own site was cited, how many sources, and the top competitors. When your own files are ready:

```bash
python3 visibility.py report
```

How to read it: **Mentions** counts how often your company name appears in the answer. **Own site** says whether your domain is among the cited sources. A `0` on a prompt that does not name you means that engine does not bring you up on its own.

---

## M5. The web page

Paste above the marker:

```python
CSS = """
:root{--bg:#0A1C36;--panel:#10264A;--line:#24406E;--ink:#FFFFFF;--mut:#9FB0C8;--blue:#3D7FFC;--pink:#EB378C}
*{box-sizing:border-box}
body{margin:0;padding:40px 20px;background:radial-gradient(900px 500px at 100% 0,#0A479C55,transparent),var(--bg);
 color:var(--ink);font:15px/1.5 Inter,system-ui,-apple-system,sans-serif}
main{max-width:1240px;margin:auto}
h1{font-size:32px;margin:0 0 4px} .sub{color:var(--mut);margin:0 0 28px}
.kpis{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:28px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 22px;min-width:190px}
.kpi b{display:block;font-size:32px} .kpi span{color:var(--mut);font-size:13px}
.wrap{overflow-x:auto} table{border-collapse:separate;border-spacing:12px;width:100%;min-width:920px}
th{text-align:left;font-size:13px;color:var(--mut);text-transform:uppercase;letter-spacing:.05em}
th.q{text-transform:none;font-size:14px;color:var(--ink);width:210px;vertical-align:top}
td{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px;vertical-align:top;font-size:13px}
td.yes{border-top:4px solid var(--blue)} td.no{border-top:4px solid var(--pink)} td.miss{color:var(--mut)}
.badge{font-weight:600;display:flex;justify-content:space-between;margin-bottom:8px}
td.yes .badge{color:#76A5FF} td.no .badge{color:var(--pink)}
.chip{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:1px 10px;margin:2px 4px 2px 0;font-size:12px}
.chip.own{border-color:#76A5FF;color:#76A5FF}
.lbl{margin-top:12px;font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut)}
.src{word-break:break-word} details{margin-top:12px} summary{cursor:pointer;color:#76A5FF} details p{color:var(--mut)}
"""


def cell_html(a):
    if a is None:
        return '<td class="miss">no data</td>'
    esc = html.escape
    named = a["mentions"] > 0
    own = ('<span class="chip own">own site cited</span>' if a["own_cited"]
           else '<span class="chip">own site not cited</span>')
    rivals = "".join(f'<span class="chip">{esc(k)} x{v}</span>' for k, v in
                     sorted(a["competitors"].items(), key=lambda kv: -kv[1])[:5]) or "<i>none</i>"
    sources = ", ".join(esc(d) for d in a["domains"][:4]) or "none"
    return (f'<td class="{"yes" if named else "no"}">'
            f'<div class="badge">{"Named" if named else "Not mentioned"}<b>{a["mentions"]}</b></div>{own}'
            f'<div class="lbl">Competitors named</div><div>{rivals}</div>'
            f'<div class="lbl">Sources ({len(a["domains"])})</div><div class="src">{sources}</div>'
            f'<details><summary>Answer</summary><p>{esc(a["text"][:1200])}</p></details></td>')


def build_html(cfg, results):
    esc = html.escape
    head = "".join(f"<th>{esc(e['name'].replace('_', ' '))}</th>" for e in cfg["engines"])
    rows = ""
    for i, prompt in enumerate(cfg["prompts"], 1):
        cells = "".join(cell_html(results[f"p{i}", e["name"]]) for e in cfg["engines"])
        rows += f'<tr><th class="q">{esc(prompt)}</th>{cells}</tr>'
    got = [a for a in results.values() if a]
    named = sum(1 for a in got if a["mentions"])
    own = sum(1 for a in got if a["own_cited"])
    rivals = {}
    for a in got:
        for k, v in a["competitors"].items():
            rivals[k] = rivals.get(k, 0) + v
    top = ", ".join(f"{k} ({v})" for k, v in sorted(rivals.items(), key=lambda kv: -kv[1])[:5]) or "none"
    return f"""<!doctype html><meta charset="utf-8"><title>AI visibility: {esc(cfg['company'])}</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><style>{CSS}</style><main>
<h1>What does AI say about {esc(cfg['company'])}?</h1>
<p class="sub">{len(cfg['prompts'])} prompts x {len(cfg['engines'])} engines, one run each. Answers vary from run to run.</p>
<div class="kpis">
<div class="kpi"><b>{named}/{len(got)}</b><span>answers name the company</span></div>
<div class="kpi"><b>{own}/{len(got)}</b><span>cite {esc(cfg['domain'])}</span></div>
<div class="kpi"><b style="font-size:17px">{esc(top)}</b><span>most-named competitors</span></div></div>
<div class="wrap"><table><tr><th></th>{head}</tr>{rows}</table></div></main>"""


def cmd_html(folder="raw"):
    """Write report.html and open it in your browser."""
    cfg, results = load_results(folder)
    out = Path("report.html").resolve()
    out.write_text(build_html(cfg, results))
    print(f"Wrote {out}")
    webbrowser.open(out.as_uri())
```

Sample data first:

```bash
python3 visibility.py html building-blocks/sample
```

Your browser opens `report.html`: a grid with a column per engine and a row per prompt. Each cell shows whether the company is named, whether its own site is cited, the competitors named and the top sources; click **Answer** to read the full text. Then the same for your own data:

```bash
python3 visibility.py html
```

If the browser does not open, open `report.html` from the repo folder yourself.

---

## Level up (optional)

Pick one if you finish early.

1. **Keep history.** Paste this above the marker, then run `python3 visibility.py save` after each run. It appends the numbers to `history.csv`, so you can compare today with next week.

```python
def cmd_save(folder="raw"):
    """Optional: append this run to history.csv, so you can compare runs over time."""
    cfg, results = load_results(folder)
    path = Path("history.csv")
    new = not path.exists()
    with path.open("a") as f:
        if new:
            f.write("date,company,prompt_id,engine,mentions,own_site_cited,sources,top_competitor\n")
        for (pid, eng), a in results.items():
            if a is None:
                continue
            top = max(a["competitors"], key=a["competitors"].get) if a["competitors"] else ""
            f.write(f"{time.strftime('%Y-%m-%d')},{cfg['company']},{pid},{eng},{a['mentions']},"
                    f"{'yes' if a['own_cited'] else 'no'},{len(a['domains'])},{top}\n")
    print(f"Appended {len(results)} rows to {path}")
```

2. **Add an engine.** Copy one more line from `building-blocks/engines.md` into `config.json`, then run `start` and `collect` again.
3. **Add a prompt.** Choose another one from `building-blocks/prompts.md`, then run the whole chain again.
4. **Run it twice.** Run `start`, `collect`, `report` a second time with a different prompt wording and compare. Answers change between runs: how stable is your result?
5. **Change the page.** Edit the `CSS` text in the HTML snippet: colours, columns, the chips. Run `html` again.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `bdata: command not found` | open a new terminal, or run `npm install -g @brightdata/cli` again |
| Login or access error | `bdata login` again; on a remote machine `bdata login --device` |
| `python3: command not found` | install Python 3.9 or later. On Windows use WSL |
| `Unknown command` | you ran a command whose snippet you have not pasted yet |
| `NameError` or `SyntaxError` | a block was pasted below the `if __name__` part. Move it above the marker line |
| `collect` waits for minutes | normal for ChatGPT and Google AI Mode. Leave it running, or continue with sample data |
| `FAILED` for one engine | skip it: the report shows "no data" for it. Try again later |
| `raw/jobs.json` not found | run `start` first |
| Report shows `no data` everywhere | `ls raw/`: the files must be named like `p1.chatgpt.json` and not be empty |
| Mentions are 0 but the answer names you | add the spelling used in the answer to `names` in `config.json` |
| Mentions are too high | your name is a common word. Keep `names` specific; matching is case-sensitive |
| Browser did not open | open `report.html` yourself |
| Typed the API key into a file or chat | rotate the key in your account settings |
