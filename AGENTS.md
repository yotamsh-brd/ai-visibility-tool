# Instructions for AI co-pilots

You are helping a workshop attendee build a script that asks Google AI Mode, ChatGPT and Gemini about their company through the Bright Data CLI and prints a normalized report.

- Read `building-blocks/scrapers.md` before doing anything: it has the dataset IDs, inputs, output fields and timings. Do not search for other scrapers.
- Use the `bdata` CLI (already logged in). Never ask for, print or store an API key.
- Scraper jobs are billed and take 45 seconds to 5 minutes. Start at most one job per engine per run, run the three in parallel, and never retry in a loop.
- Records contain huge fields (`answer_html`, `response_raw`, 1 to 2 MB). Never print a whole record; select fields.
- Follow the milestones in `PROMPT.md` and stop after each one.
- `solution/` is the host's reference. Do not read or copy it unless the attendee asks.
