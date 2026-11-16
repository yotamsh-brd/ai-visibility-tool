# CLI cheat sheet (no AI needed)

Replace `AI21 Labs` with your company. Needs `bdata` and `jq`.

## Milestone 1: Ask

Start all three. They run in the background and take 1 to 5 minutes.

```bash
mkdir -p raw
COMPANY="AI21 Labs"
PROMPT="What is $COMPANY known for, and who are its main competitors?"

bdata pipelines run gd_m7aof0k82r803d5bjm collect_by_url "https://chatgpt.com/" --prompt "$PROMPT" --timeout 900 --json > raw/chatgpt.json &
bdata pipelines run gd_mbz66arm2mf9cu856y collect_by_url "https://gemini.google.com/" --prompt "$PROMPT" --timeout 900 --json > raw/gemini.json &
bdata pipelines run gd_mcswdt6z2elth3zqr2 collect_by_url "https://google.com/aimode" --prompt "$PROMPT" --timeout 900 --json > raw/google_ai_mode.json &
```

Look at what came back (when `raw/google_ai_mode.json` is not empty):

```bash
jq '.[0] | keys' raw/google_ai_mode.json
jq -r '.[0].answer_text' raw/google_ai_mode.json | head -c 600
jq '.[0].citations[0:3]' raw/google_ai_mode.json
```

## Milestone 2: Report

Same loop, any folder. Use `RAW=building-blocks/samples` while your own files are still loading.

```bash
RAW=raw
{
  printf 'Engine\tMentions\tSources\tTop sources\n'
  for e in google_ai_mode chatgpt gemini; do
    jq -r --arg e "$e" --arg c "$COMPANY" '
      .[0] | [ $e,
        ([.answer_text | scan("(?i)" + $c)] | length),
        ((.citations // []) | length),
        ([(.citations // [])[].url | capture("//(www\\.)?(?<d>[^/]+)").d]
          | reduce .[] as $d ([]; if index($d) then . else . + [$d] end) | .[0:3] | join(", ")) ] | @tsv
    ' "$RAW/$e.json" 2>/dev/null || printf '%s\tFAILED\t-\t-\n' "$e"
  done
} | column -t -s "$(printf '\t')"
```

## Milestone 3: One command

Put the Milestone 1 commands (add `wait` after them) and the Milestone 2 loop in one file, `report.sh`, taking the company as `$1`:

```bash
chmod +x report.sh
./report.sh "Your Company"
```

Stuck? The host has a working version in `solution/`.
