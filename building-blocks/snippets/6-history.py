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


# >>> paste the next snippet above this line <<<
