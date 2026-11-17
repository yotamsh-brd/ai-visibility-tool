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


# >>> paste the next snippet above this line <<<
