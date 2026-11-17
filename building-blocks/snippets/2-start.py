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


# >>> paste the next snippet above this line <<<
