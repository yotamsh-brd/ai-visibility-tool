# The three scrapers

All three use the method `collect_by_url` with two required inputs: `url` (fixed per engine) and `prompt` (your question).

| Engine | `dataset_id` | `url` input | Time seen on 16/11/2026 |
| --- | --- | --- | --- |
| Google AI Mode | `gd_mcswdt6z2elth3zqr2` | `https://google.com/aimode` | 45 to 123 s |
| Gemini | `gd_mbz66arm2mf9cu856y` | `https://gemini.google.com/` | 121 to 150 s |
| ChatGPT | `gd_m7aof0k82r803d5bjm` | `https://chatgpt.com/` | about 300 s |

Times are from a handful of runs and vary; plan for up to 5 minutes.

## Call one

```bash
bdata pipelines run gd_mcswdt6z2elth3zqr2 collect_by_url "https://google.com/aimode" \
  --prompt "What is AI21 Labs known for, and who are its main competitors?" \
  --timeout 900 --json > raw/google_ai_mode.json
```

The command waits until the answer is ready. Progress goes to stderr, the JSON to stdout. If you stop waiting, it prints a snapshot ID; fetch the data later with `bdata pipelines results <snapshot_id> --json`.

## What comes back

A JSON array with one record. Fields every engine has:

| Field | What it is |
| --- | --- |
| `prompt` | The question you sent |
| `answer_text` | The answer as plain text (includes link labels such as "Docs +1") |
| `answer_text_markdown` | The same answer as markdown |
| `citations` | List of `{url, title, domain, cited}`; may be empty |
| `timestamp` | When it was collected |

Ignore `answer_html` and `response_raw`: 1 to 2 MB each. Engine extras: ChatGPT has `web_search_triggered`, `shopping`, `links_attached`; Google AI Mode has `links_attached`, `citations_mapping`; Gemini has `model`.

## Gotchas

- ChatGPT citation URLs end in `?utm_source=chatgpt.com`. Take the domain from `url`, not the full link.
- Some Gemini citations have `cited: false` (listed as a source, not directly quoted).
- Run the same prompt twice and mentions, sources and even whether your own site is cited can change.
- `bdata budget` can return 403 with a restricted key. Use `bdata pipelines search chatgpt` to check that you are logged in.
- Optional inputs: `country` (all three), `web_search` and `additional_prompt` (ChatGPT).

## The normalized report

Per engine: status, seconds, mentions of the company in `answer_text`, number of citations, source domains (de-duplicated, in order), and whether your own domain is cited. Across engines: domains cited by 2 or more.
