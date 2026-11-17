# What does AI say about your company when you're not in the room?

In this hands-on session you build a small tool that asks several AI engines (ChatGPT, Gemini, Google AI Mode, Bing Copilot) the same questions about **your own company**, and turns their answers into a web page: is your company named, which competitors come up, and which websites the engines trust.

You choose the engines, the questions and what to measure. About 60 minutes, no prior scraping knowledge needed.

**Finish line:** open `building-blocks/sample-report.html` in your browser to see what you are building.

## How the session works

| Time | What you do |
|---|---|
| 0:00 to 0:05 | The host introduces the session and shows the finish line |
| 0:05 to 0:15 | **Get ready** (steps 1 to 5): get the repo, install the Bright Data CLI, log in |
| 0:15 to 0:28 | **Choose** (steps 6 to 9): browse the scraper library, pick your engines, your company and your prompts |
| 0:28 to 0:50 | **Build** (steps 10 to 14): write the script in five small steps, run it, open your report |
| 0:50 to 1:00 | **Read and share**: what surprised you? |

You can build in two ways, and both end at the same report:

- **By hand.** Follow this page and copy the code blocks from [`CHEATSHEET.md`](CHEATSHEET.md).
- **With an AI co-pilot** (Claude Code, Cursor, Copilot, Codex, ...). Open this folder in your editor, paste the contents of [`PROMPT.md`](PROMPT.md), and the co-pilot walks you through the same steps, asking you the same questions.

## What you need

- A laptop with a terminal: macOS, Linux, or Windows with WSL.
- **Node.js 20 or later** (`node --version`) and **Python 3.9 or later** (`python3 --version`).
- **git** and **curl** (both come with macOS and most Linux systems).
- A Bright Data account.
- A text editor (VS Code or anything else).

## Part 1: Get ready (about 10 minutes)

### Step 1. Get the repo and open a terminal in it

If you have not cloned it yet:

```bash
git clone https://github.com/yotamsh-brd/ai-visibility-tool.git
cd ai-visibility-tool
ls
```

You should see `README.md`, `CHEATSHEET.md`, `PROMPT.md`, `config.json`, `building-blocks/` and `solution/`. **Every command in this guide runs from this folder.** If you open a new terminal window later, `cd` back into it first.

> Please do not open `solution/` yet. It holds the finished script, and you learn more by building it.

### Step 2. Install the Bright Data CLI

```bash
node --version
npm install -g @brightdata/cli
bdata --version
```

`node --version` must show `v20` or higher. The last command prints a version number such as `0.4.1`. If it says `command not found`, close the terminal, open a new one and try again.

### Step 3. Log in and check that it works

```bash
bdata login
bdata pipelines search chatgpt
```

`bdata login` opens your browser: sign in and approve. On a remote machine use `bdata login --device` instead.

The second command should print a short list that includes `ChatGPT Search` with a dataset id starting `gd_`. That list means you are logged in and can see the scrapers.

Co-pilot users: also run `npx skills add brightdata/skills -g`.

### Step 4. Check Python

```bash
python3 --version
```

It must show 3.9 or higher. You do not need to install any packages: the script uses only what comes with Python.

### Step 5. Look at the finish line

Open `building-blocks/sample-report.html` in your browser (double-click it). Spend two minutes with it: each column is an AI engine, each row is a question, and each cell tells you whether the company was named, which competitors appeared and which sources were used. This is real data collected for a real company. Your job is to produce the same page for **your** company.

## Part 2: Choose (about 13 minutes)

All your choices go into one file, `config.json`. You fill it in during these steps.

### Step 6. Pick your engines

1. Open the scraper library: <https://brightdata.com/cp/scrapers/browse?category=all>
2. Search for the AI engines and look at what each one takes as input (a `url` and a `prompt`) and what it returns (the answer and its sources).
3. Choose **two or three** engines. Open [`building-blocks/engines.md`](building-blocks/engines.md): it has a ready-to-paste line for each engine (name, dataset id and url).

| Engine | Starts with |
|---|---|
| Google AI Mode | CLI |
| ChatGPT | CLI |
| Gemini | CLI |
| Bing Copilot | REST: needs an API key |

**If you choose Bing Copilot** you need an API key, because the CLI does not know this new scraper yet and the script starts it through the REST API instead:

1. Create an API key in your Bright Data account settings.
2. In the terminal you will use for the "start" step, run: `export BRIGHTDATA_API_KEY="paste-your-key"`
3. Never paste the key into a file in this folder, into a chat or on a shared screen. If you do, rotate it right away.

More engines means more waiting and more cost, so two or three is plenty. You can add more later.

### Step 7. Name your company

You need four things:

- **company**: the name as you would say it, for example `Wonderful AI`.
- **domain**: your website without `https://` or `www.`, for example `wonderful.ai`.
- **names**: every way your company is written in text, for example `["Wonderful AI", "Wonderful"]`. Matching is case-sensitive.
- **competitors**: three to ten companies you want counted, for example `["Sierra", "Decagon", "Parloa"]`.

No company at hand? Use any public company you know well.

### Step 8. Choose your prompts

Open [`building-blocks/prompts.md`](building-blocks/prompts.md), pick **two** prompts and fill in the blanks (or write your own). Make sure at least one prompt does **not** contain your company name: for example "What are the best [your category] for [your customer type]?". That is the prompt that tells you whether AI recommends you without being asked.

### Step 9. Write `config.json`

Open `config.json` in your editor. It comes with placeholder values (`Your Company`, `yourcompany.com`, ...): replace every value with your choices from steps 6 to 8. [`CHEATSHEET.md`](CHEATSHEET.md#1-fill-in-configjson) explains each key.

JSON rules: use double quotes, put a comma between entries, and **no comma after the last entry**.

## Part 3: Build (about 22 minutes)

You build one script, `visibility.py`, in five steps. Each step adds one command and you run it straight away. All the code is in [`CHEATSHEET.md`](CHEATSHEET.md): copy it from there.

**Rule for pasting:** the first block creates the file. Every later block goes **above** the line `# >>> paste the next snippet above this line <<<`, so the last lines of the file always stay at the bottom.

### Step 10. M1: the skeleton

Create `visibility.py`, paste the M1 block, and run:

```bash
python3 visibility.py plan
```

You should see your company, how many jobs will run (prompts x engines) and one line per job. Nothing has been sent yet and it costs nothing. If something looks wrong, fix `config.json` now.

### Step 11. M2: start the jobs

Paste the M2 block, then run:

```bash
python3 visibility.py start
```

You should see one `started` line per job, each with an id starting `sd_`. The work now happens on Bright Data's side, in parallel. **Run `start` only once**: every run starts, and bills, new jobs.

### Step 12. M3: collect the answers

Paste the M3 block, then run:

```bash
python3 visibility.py collect
```

It checks every ten seconds and prints a `done` line when an answer arrives. Expect one to three minutes for the first answers; ChatGPT and Google AI Mode can take up to ten. **Do not wait with your arms crossed.** Open a second terminal, `cd` into the folder and continue with steps 13 and 14 using the sample data (see below). If you close the terminal by accident, run `collect` again: it skips what it already saved.

### Step 13. M4: the analysis

Paste the M4 block, then try it on the sample data so you do not have to wait:

```bash
python3 visibility.py report building-blocks/sample
```

You should see a table with one line per prompt and engine. When your own answers have arrived:

```bash
python3 visibility.py report
```

### Step 14. M5: the web page

Paste the M5 block, then:

```bash
python3 visibility.py html building-blocks/sample
python3 visibility.py html
```

The first line opens the sample page, the second one opens **your** report.

## Part 4: Read your report

Look at the grid and answer these questions:

1. **Does each engine name your company?** Compare the prompt with your name and the prompt without it.
2. **Who shows up instead of you?** Look at the competitors in the cells where you are not named.
3. **Is your own website among the cited sources?** If not, which sites are cited instead? Those are the sites that shape what AI says about you.
4. **Do the engines agree?** Rarely. That is the finding.

A note of caution: run the same prompt again and the answer, the sources and the counts change. One run is a snapshot, not a verdict. If something looks surprising, run it a second time before drawing conclusions.

## Part 5: Level up (if you finish early)

See "Level up" in [`CHEATSHEET.md`](CHEATSHEET.md#level-up-optional): keep a `history.csv` to compare runs over time, add an engine, add a prompt, run twice and compare, or restyle the page.

## Something went wrong?

The troubleshooting table at the end of [`CHEATSHEET.md`](CHEATSHEET.md#troubleshooting) covers the common problems. Otherwise raise your hand: the host has a working version.

## What is in this repo

| Path | What it is |
|---|---|
| `README.md` | this guide |
| `CHEATSHEET.md` | all the code and commands you copy, in order |
| `PROMPT.md`, `AGENTS.md` | for building with an AI co-pilot |
| `building-blocks/engines.md` | the engines: dataset ids, inputs, REST snippet |
| `building-blocks/prompts.md` | a menu of prompts |
| `building-blocks/sample/` | real sample answers, to work with while yours load |
| `building-blocks/sample-report.html` | the finish line |
| `building-blocks/snippets/` | the code blocks as separate files |
| `solution/visibility.py` | the finished script (look at the end) |

Safety: never put your API key in this folder. The `.gitignore` already excludes `raw/`, `report.json` and `.env` files, but it cannot protect a key you paste into another file.
