# The AI engines (Bright Data scrapers)

Every engine below is a Bright Data scraper that takes two inputs, `url` and `prompt`, and returns the answer text and the sources the engine cited.

Browse them yourself first: <https://brightdata.com/cp/scrapers/browse?category=all> (search for the name, or for the domain in the last column).

## Pick your engines

| Engine | Dataset ID | `url` input | Typical time* | Start it with |
|---|---|---|---|---|
| Google AI Mode | `gd_mcswdt6z2elth3zqr2` | `https://google.com/aimode` | 1 to 11 min | CLI |
| ChatGPT | `gd_m7aof0k82r803d5bjm` | `https://chatgpt.com/` | 1 to 10 min | CLI |
| Gemini | `gd_mbz66arm2mf9cu856y` | `https://gemini.google.com/` | 1 to 3 min | CLI |
| Bing Copilot | `gd_mwccaeuk8oyhtzmkf` | `https://www.bing.com/copilotsearch` | 1 to 3 min | REST (needs an API key) |

\*Times vary a lot from run to run. Start everything at once and do something else while it runs.


## Paste-ready lines for `config.json`

Copy the lines of the engines you want into the `"engines"` list (commas between entries, none after the last one):

```json
{"name": "google_ai_mode", "dataset_id": "gd_mcswdt6z2elth3zqr2", "url": "https://google.com/aimode"},
{"name": "chatgpt", "dataset_id": "gd_m7aof0k82r803d5bjm", "url": "https://chatgpt.com/"},
{"name": "gemini", "dataset_id": "gd_mbz66arm2mf9cu856y", "url": "https://gemini.google.com/"},
{"name": "bing_copilot", "dataset_id": "gd_mwccaeuk8oyhtzmkf", "url": "https://www.bing.com/copilotsearch", "trigger": "rest"}
```

`"name"` is only a label (letters and underscores) and becomes part of the file names in `raw/`.
`"trigger": "rest"` tells the script to start that engine through the REST API instead of the CLI. Only Bing Copilot needs it.

## Why Bing Copilot uses REST

The CLI keeps its own list of scrapers, and Bing Copilot Search was added only a few days ago, so some CLI versions reject its ID ("Unknown dataset_id"). The REST API accepts it. Everything after the start (checking progress, downloading the result) works through the CLI for every engine.

### Start Bing Copilot by hand (REST)

```bash
export BRIGHTDATA_API_KEY="paste-your-key-here"   # create one in your Bright Data account settings

curl -s -X POST "https://api.brightdata.com/datasets/v3/trigger?dataset_id=gd_mwccaeuk8oyhtzmkf&include_errors=true" \
  -H "Authorization: Bearer $BRIGHTDATA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"url": "https://www.bing.com/copilotsearch", "prompt": "What is Wonderful AI known for?"}]'
```

You get back `{"snapshot_id":"sd_..."}`. Then:

```bash
bdata pipelines status sd_XXXX        # "running" or "ready"
bdata pipelines results sd_XXXX --json > raw/bing.json
```

Never paste your API key into a chat, a screenshot or a file inside this repo. If you did, rotate it in your account settings.

## What comes back

One list with one record per prompt. These fields exist for every engine:

| Field | What it is |
|---|---|
| `prompt` | the question you asked |
| `answer_text` | the answer as plain text |
| `answer_text_markdown` | the same answer with formatting |
| `citations` | list of `{url, title, domain, ...}`: the sources the engine used |
| `timestamp` | when the answer was produced |

Every record also contains `answer_html` (often 1 to 3 MB) and, for some engines, `response_raw`. Never print them: they will flood your terminal and your co-pilot's context.

## Good to know

- **Answers change between runs.** The same prompt on the same engine can give different companies and different sources an hour later. One run is a snapshot, not a verdict.
- **Citation URLs differ in shape.** Google AI Mode returns only the site (`https://cloud.google.com`), ChatGPT adds `?utm_source=chatgpt.com`. The script compares domains only.
- **Short or empty answers happen.** Some prompts return a one-line answer. The report shows the number anyway.
- **Company names that are common words** ("Wonderful", "Apple", "Notion") also match ordinary sentences. List every way the name is written in `"names"`. Matching is case-sensitive, so "wonderful" the adjective is ignored.
