#!/usr/bin/env bash
# CLI-only version (needs bdata and jq).
#   ./report.sh "AI21 Labs"                                          # asks the 3 engines live
#   RAW=../building-blocks/samples ./report.sh "AI21 Labs"           # offline, uses saved answers
set -u
COMPANY="${1:?usage: ./report.sh \"Company name\"}"
PROMPT="What is $COMPANY known for, and who are its main competitors?"
RAW="${RAW:-raw}"

if [ "$RAW" = raw ]; then
  mkdir -p raw
  ask () { bdata pipelines run "$2" collect_by_url "$3" --prompt "$PROMPT" --timeout 900 --json > "raw/$1.json" & }
  ask google_ai_mode gd_mcswdt6z2elth3zqr2 https://google.com/aimode
  ask chatgpt        gd_m7aof0k82r803d5bjm https://chatgpt.com/
  ask gemini         gd_mbz66arm2mf9cu856y https://gemini.google.com/
  echo "Asking 3 engines in parallel (1 to 5 minutes)..."
  wait
fi

printf '\nAI VISIBILITY REPORT: %s\nPrompt: %s\n\n' "$COMPANY" "$PROMPT"
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
