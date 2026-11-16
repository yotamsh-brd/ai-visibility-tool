# What does AI say about your company when you're not in the room?

45-minute hands-on. You will build a small script: **one command asks Google AI Mode, ChatGPT and Gemini the same question about your company and prints a short report.**

```
$ ./report.sh "Your Company"

Engine          Mentions  Sources  Top sources
google_ai_mode  7         3        aionx.co, docs.ai21.com, vantaige.io
chatgpt         6         13       aws.amazon.com, companyview.io, benched.ai
gemini          5         6        g2.com, tracxn.com, research.contrary.com
```

A fuller example (with timings and answer excerpts): [building-blocks/sample-report.txt](building-blocks/sample-report.txt)

## Setup (about 5 minutes)

You need a [Bright Data](https://brightdata.com) account, Node.js 20+, Python 3.9+ and a terminal (macOS, Linux or WSL).

```bash
npm install -g @brightdata/cli
bdata login
bdata pipelines search chatgpt        # must print "ChatGPT Search"
```

Using an AI co-pilot (Claude Code, Cursor, Codex)? Also run: `npx skills add brightdata/skills -g`

## Build it in 3 milestones

| | Milestone | Done when |
| --- | --- | --- |
| 1 | **Ask**: get one raw answer from a scraper, start the other two | `raw/google_ai_mode.json` exists and you can name 3 of its fields |
| 2 | **Report**: print a normalized report from the files in `raw/` | You see a table with mentions and sources per engine |
| 3 | **One command**: the script asks the three engines itself | One command goes from company name to report (`./report.sh "Your Company"` or your own script) |

Two ways to build, same milestones:

- **With an AI co-pilot:** open this folder in your agent and paste [PROMPT.md](PROMPT.md). It stops after each milestone.
- **With CLI commands:** follow [CHEATSHEET.md](CHEATSHEET.md).

Stuck? Everything about the scrapers (IDs, inputs, fields, timings) is in [building-blocks/scrapers.md](building-blocks/scrapers.md). Waiting for answers? Use `building-blocks/samples/` (real saved answers) to build milestone 2 right away.

## Good to know

- One run = 3 scraper records on your account.
- Answers take **45 seconds to 5 minutes**; ChatGPT is usually the slowest. Start it first.
- Run it twice and you will get different answers. That is part of the point.
