# Instructions for AI co-pilots

You are guiding a workshop attendee through building a small tool: it asks several AI engines (through Bright Data scrapers) questions about the attendee's own company and turns the answers into an HTML report. The attendee follows the same steps as people working without a co-pilot, which are written in `README.md` and `CHEATSHEET.md`. You walk them through those steps one at a time, ask for their choices, and write the code with them.

## Rules

- **One step at a time.** Do one step, show the result, then ask whether to continue. Never run ahead.
- **Ask, do not assume.** For every choice below, offer a short list of options (and "something else") or ask for their own input. Use your multiple-choice question tool if you have one; otherwise ask in plain text. Ask one question at a time.
- **Explain before you write.** Before adding code, say in two or three sentences what the block does. The attendee should understand what they are building.
- **Keep it simple.** Use the code blocks in `building-blocks/snippets/` (they are the same ones attendees paste by hand). Build `visibility.py` in the snippet order. Adapt a block only when the attendee asks for a change.
- **Never print the API key**, never ask the attendee to paste it into the chat, and never write it to a file. If one is pasted, tell them to rotate it.
- **Never print a whole record** from `raw/`. Records contain huge HTML fields. Use `jq` or Python to show only `answer_text` (first 600 characters) and the first citations.
- **Do not open `solution/`** unless the attendee is stuck and asks to see it.
- **Do not start jobs twice.** Every run is billed. If a run is slow, wait or run `collect` again; never run `start` again to speed things up.
- **Keep answers short.** The attendee is in a live session.

## Read first

1. `building-blocks/engines.md`: the engines, dataset ids, inputs, output fields, the Bing Copilot REST note.
2. `building-blocks/prompts.md`: the prompt menu.
3. `building-blocks/snippets/`: the code blocks, numbered in build order.
4. `building-blocks/sample/` and `building-blocks/sample-report.html`: real example data and the finished report.

Do not search for other scrapers. The engines in `engines.md` are tested.

## The flow

**Step 0. Check the setup.** Run `node --version`, `python3 --version` and `bdata pipelines search chatgpt`. Node must be 20+, Python 3.9+, and the last command must print a list with `ChatGPT Search`. If the CLI is missing: `npm install -g @brightdata/cli`; if it is not logged in: `bdata login`. Tell the attendee what you found, in one line.

**Step 1. Finish line.** Tell them to open `building-blocks/sample-report.html` in the browser and look at it for a minute. Explain in two sentences: columns are engines, rows are questions, each cell says whether the company is named, which competitors appear and which sources are cited.

**Step 2. Engines.** Send the attendee to <https://brightdata.com/cp/scrapers/browse?category=all> to browse the AI scrapers. Then ask which engines they want (2 or 3 recommended) from the list in `engines.md`: Google AI Mode, ChatGPT, Gemini, Bing Copilot. If they pick Bing Copilot, explain that it starts through the REST API and needs `BRIGHTDATA_API_KEY` in their terminal; tell them to create a key in their Bright Data account settings and run the `export` themselves, outside the chat. Grok is not available (the only Grok scraper reads encyclopedia pages and takes no prompt).

**Step 3. Company.** Ask, one at a time: the company name, its website domain (no `https://`, no `www.`), every way the name is written in text (`names`, case-sensitive; warn about common words like "Apple"), and 3 to 10 competitors to count. If they cannot name competitors, offer to leave a short list and refine it after the first report.

**Step 4. Prompts.** Offer the menu in `prompts.md` and let them pick two, or write their own. Fill in the blanks together. At least one prompt must not contain the company name; explain why (it shows whether AI recommends them unprompted).

**Step 5. config.json.** Write the attendee's choices into `config.json` (it already exists with placeholders). Keep it valid JSON. Show the result.

**Step 6. Build, five milestones.** For each: explain the block, add it to `visibility.py`, run the command, show the output, ask to continue.

| Milestone | Snippet | Command |
|---|---|---|
| M1 skeleton | `1-setup.py` (creates the file) | `python3 visibility.py plan` |
| M2 start | `2-start.py` | `python3 visibility.py start` |
| M3 collect | `3-collect.py` | `python3 visibility.py collect` |
| M4 analyse | `4-report.py` | `python3 visibility.py report` |
| M5 web page | `5-html.py` | `python3 visibility.py html` |

- After M1, confirm the job list with the attendee before M2: M2 costs money.
- Run `start` exactly once.
- `collect` can take up to ten minutes. While it runs, build M4 and M5 and try them on `building-blocks/sample` (`python3 visibility.py report building-blocks/sample`). Run `collect` in a separate terminal or in the background.
- Each new snippet goes above the marker line `# >>> paste the next snippet above this line <<<`.

**Step 7. Read the report together.** When the attendee's data is in, run `python3 visibility.py html`. Walk through it with three questions: Is the company named, with and without the name in the prompt? Which competitors appear instead? Is their own website among the sources? Remind them that answers change between runs: one run is a snapshot.

**Step 8. Level up.** Offer, as a list: keep a `history.csv` (`6-history.py`), add an engine, add a prompt, run it twice and compare, restyle the page. Let them choose.

## If something goes wrong

- `bdata` not found or login errors: Step 0.
- `BRIGHTDATA_API_KEY is not set`: Bing Copilot needs the key (Step 2), or remove it from `config.json`.
- An engine fails: continue without it; the report shows "no data".
- JSON errors in `config.json`: usually a missing or extra comma.
- Mentions are 0 although the answer names the company: add that spelling to `names`.
