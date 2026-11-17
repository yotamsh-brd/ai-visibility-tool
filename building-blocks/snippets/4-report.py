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


# >>> paste the next snippet above this line <<<
