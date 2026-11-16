#!/usr/bin/env python3
"""What does AI say about your company? Ask Google AI Mode, ChatGPT and Gemini, print one report.

  python3 ai_visibility.py "AI21 Labs" --domain ai21.com
  python3 ai_visibility.py "AI21 Labs" --samples ../building-blocks/samples   # offline, no credits

Needs the Bright Data CLI, logged in once with:  bdata login
"""
import argparse, json, re, shutil, subprocess, sys, time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

ENGINES = {  # name: (dataset id, url input, sample file)
    "Google AI Mode": ("gd_mcswdt6z2elth3zqr2", "https://google.com/aimode", "google_ai_mode"),
    "ChatGPT": ("gd_m7aof0k82r803d5bjm", "https://chatgpt.com/", "chatgpt"),
    "Gemini": ("gd_mbz66arm2mf9cu856y", "https://gemini.google.com/", "gemini"),
}
PROMPT = "What is {company} known for, and who are its main competitors?"
SHORT = {"google": "Google AI Mode", "chatgpt": "ChatGPT", "gemini": "Gemini"}


def ask(engine, prompt, samples):
    """One scraper call. Blocks until the answer is ready (45 s to 5 min). Returns (record, seconds)."""
    dataset, url, sample = ENGINES[engine]
    if samples:
        return json.loads((Path(samples) / f"{sample}.json").read_text())[0], None
    cli = shutil.which("bdata") or shutil.which("brightdata")
    if not cli:
        raise RuntimeError("Bright Data CLI not found: npm install -g @brightdata/cli")
    start = time.time()
    run = subprocess.run(
        [cli, "pipelines", "run", dataset, "collect_by_url", url,
         "--prompt", prompt, "--timeout", "900", "--json"],
        capture_output=True, text=True)
    if run.returncode != 0:
        raise RuntimeError((run.stderr or run.stdout).strip()[-200:] or "CLI failed")
    records = json.loads(run.stdout)
    if not records or records[0].get("error"):
        raise RuntimeError(str(records[:1])[:200])
    return records[0], round(time.time() - start)


def domain(url):
    return urlparse(url).netloc.lower().removeprefix("www.")


def normalize(engine, company, own_domain, record, seconds):
    """Same few fields for every engine, whatever the scraper returned."""
    answer = " ".join((record.get("answer_text") or record.get("answer_text_markdown") or "").split())
    domains = list(dict.fromkeys(domain(c["url"]) for c in record.get("citations") or [] if c.get("url")))
    return {
        "engine": engine, "status": "ok", "seconds": seconds, "answer": answer,
        "mentions": len(re.findall(re.escape(company), answer, re.I)),
        "citations": len(record.get("citations") or []), "domains": domains,
        "own_site_cited": bool(own_domain) and any(d.endswith(own_domain) for d in domains),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("company")
    ap.add_argument("--domain", default="", help="company website, e.g. ai21.com")
    ap.add_argument("--prompt", default=PROMPT, help="use {company} as the placeholder")
    ap.add_argument("--samples", help="folder with saved answers: skips the scrapers")
    ap.add_argument("--engines", default="google,chatgpt,gemini", help="comma list; google is the fastest (~45 s)")
    ap.add_argument("--out", default="report.json", help="where to save the normalized data")
    args = ap.parse_args()
    prompt = args.prompt.format(company=args.company)
    own = args.domain.lower().removeprefix("www.")
    engines = [SHORT[k.strip()] for k in args.engines.split(",")]

    print(f"Asking {len(engines)} engines in parallel: {prompt!r}\nAnswers take 1 to 5 minutes (ChatGPT is usually the slowest).", flush=True)

    def one(engine):
        try:
            record, secs = ask(engine, prompt, args.samples)
            print(f"  {engine}: answer received", flush=True)
            return normalize(engine, args.company, own, record, secs)
        except Exception as exc:
            print(f"  {engine}: failed", flush=True)
            return {"engine": engine, "status": f"failed: {exc}", "seconds": None, "answer": "",
                    "mentions": 0, "citations": 0, "domains": [], "own_site_cited": False}

    with ThreadPoolExecutor(len(engines)) as pool:
        rows = list(pool.map(one, engines))
    Path(args.out).write_text(json.dumps({"company": args.company, "prompt": prompt, "results": rows},
                                         ensure_ascii=False, indent=2))

    print(f"\nAI VISIBILITY REPORT: {args.company}\nPrompt: {prompt}\n")
    print(f"{'Engine':<16}{'Status':<8}{'Time':>6}{'Mentions':>10}{'Sources':>9}  Own site cited")
    for r in rows:
        status = "ok" if r["status"] == "ok" else "FAILED"
        own_flag = "-" if not own else ("yes" if r["own_site_cited"] else "no")
        secs = "-" if r["seconds"] is None else f"{r['seconds']}s"
        print(f"{r['engine']:<16}{status:<8}{secs:>6}{r['mentions']:>10}{r['citations']:>9}  {own_flag}")
    for r in rows:
        print(f"\n--- {r['engine']}")
        print(r["answer"][:300] + ("..." if len(r["answer"]) > 300 else "") if r["status"] == "ok" else r["status"])
        if r["domains"]:
            print("Top sources: " + ", ".join(r["domains"][:5]))
    shared = [d for d, n in Counter(d for r in rows for d in r["domains"]).items() if n > 1]
    print("\nSources cited by 2+ engines: " + (", ".join(shared) if shared else "none"))
    print(f"\nFull data saved to {args.out}")


if __name__ == "__main__":
    sys.exit(main())
