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


# >>> paste the next snippet above this line <<<
