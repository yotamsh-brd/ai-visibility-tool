# Prompt menu

Pick two or three, or write your own. Replace the words in `[brackets]`, then paste the result into the `"prompts"` list of `config.json`.

| # | Prompt | What it tells you |
|---|---|---|
| 1 | What is [company] known for, and who are its main competitors? | Does AI know you, and who does it put next to you? |
| 2 | What are the best [your category] for [your customer type]? | Are you in the shortlist when nobody names you? |
| 3 | Is [company] a good choice for [use case]? What are the alternatives? | How does AI sell you against alternatives? |
| 4 | [company] vs [competitor]: which is better, and why? | How does AI compare you head to head? |
| 5 | What do customers say about [company]? Any common complaints? | What does AI repeat about your reputation? |
| 6 | I need [what your customer wants to do]. Which tools or vendors should I look at? | Do you show up for a buyer who does not know you yet? |

**Tip:** always include one prompt that does not contain your company name (2 or 6). That is where you find out whether AI recommends you.

Example for a company called Wonderful AI that sells AI agents for customer service:

```json
"prompts": [
  "What is Wonderful AI known for, and who are its main competitors?",
  "What are the best AI agent platforms for customer service automation in large enterprises?"
]
```

Each extra prompt multiplies the jobs (prompts x engines), the waiting time and the cost. Two prompts is plenty for today.
