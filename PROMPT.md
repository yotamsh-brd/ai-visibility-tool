# Prompt for your AI co-pilot

Open this folder in your agent (Claude Code, Cursor, Codex), replace `<COMPANY>` at the bottom, and paste everything in the block.

```text
Help me build a small script in this folder. First read AGENTS.md and building-blocks/scrapers.md.

Goal: one command takes a company name, asks Google AI Mode, ChatGPT and Gemini the same question through the Bright Data CLI (bdata, already logged in), and prints a short normalized report.

Work in three milestones. After each one, show me the result and wait until I say "next".

1. ASK. Run the Google AI Mode scraper once for my company with the prompt "What is <COMPANY> known for, and who are its main competitors?". Save the JSON to raw/google_ai_mode.json and tell me which fields it contains. Start ChatGPT and Gemini the same way, in the background, into raw/chatgpt.json and raw/gemini.json (they take 2 to 5 minutes). Do not wait for them.

2. REPORT. Write a script that reads the three files in raw/ (use building-blocks/samples/ for any that are not ready) and prints one report: for each engine, how many times the company is mentioned, how many sources it cites and the top 3 source domains; then the domains cited by 2 or more engines. Ignore the huge answer_html field.

3. ONE COMMAND. Make the script call the three scrapers itself, in parallel, with a 15-minute timeout, so that one command goes from company name to report. If an engine fails, show it as FAILED and keep going.

Rules: start at most one job per engine per run. Never print or ask for my API key. Keep the script under about 100 lines. Use any language I have installed.

My company: <COMPANY>
```
