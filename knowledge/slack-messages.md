# Skill: Draft Slack Messages

## What this covers
Drafting Slack messages on Maarten's behalf: announcements, DMs, thread replies, data updates,
PR review requests, and A/B test result posts. Messages must sound like Maarten wrote them.

## When to use
Any Slack communication — channel posts, direct messages, thread replies, launch announcements,
PR review requests, or results posts.

## CRITICAL — Approval required before ANY send

**NEVER send a Slack message without Maarten's explicit approval. No exceptions.**

Approval workflow:
1. Post the draft to the designated **private review channel** (TBD — confirm channel name with Maarten)
2. Wait for Maarten to react with ✅ or a send emoji to approve
3. Only then send the actual message to the intended recipient/channel

This applies to ALL message types: DMs, channel posts, thread replies, PR review requests.

## How to do it

1. **Identify message type**: announcement / DM update / thread reply / A/B result / alert
2. **Identify audience**: Dutch 1:1 or English channel/group?
3. **Select template** from the reference section below
4. **Draft** following the template — BLUF structure, correct tone, emoji rules
5. **Review**: does it sound like Maarten? Is the data specific? Does it end with a hook?
6. Show draft with `STATUS: NEEDS_APPROVAL` and wait for approval before sending

### Execution tools

#### Read channel context (if needed)
```
skill: read-slack-channel
```

#### Send message
```
skill: send-slack-message
```
**Only invoke after Maarten has approved the draft.**

---

## Reference: Conventions & Patterns

### Language Rules
- **Dutch**: close 1:1 DMs (JJ, Willemijn, Mart, direct daily colleagues)
- **English**: any channel with 3+ people, cross-functional audiences, Calcite channel
- **Rule of thumb**: if in doubt → English
- Confluence, slides, analysis outputs: always English

### Structure
- BLUF: decision/headline first, justification after — never bury the conclusion
- Section headers in public channels: bold + backtick + emoji
  e.g. `:mag: *\`Why reconsider?\`*`
- Plain labels in DMs (no special formatting)
- @mentions at the top of announcements

### Tone
- Professional but direct — no corporate filler
- Balanced: acknowledge trade-offs, never absolute
- Forward-looking closing: "WDYT?", "Keep an eye out!", "Curious what you think!"
- Transparent about constraints: state honest reason if delayed, commit to specific next action

### Data
- Always back decisions with specific numbers ("43K customers", "0.05 adds", "25%")
- Use concrete customer counts not just percentages
- Define methodology before stating results

### Emoji
- **Purposeful only**: signal message type, not enthusiasm
- Launch/announcement: `:rocket:` in title, `:rolled_up_newspaper: :eyes:` at close
- Document links: `:powerpoint:` `:slack:` `:github:` as inline labels
- **Zero emoji** in analytical or decision messages

### Length
- Short thread reply: 3–4 sentences
- Team announcement: 150–250 words, clear sections
- Strategic analysis: comprehensive OK, but prefer linking to a deck over full prose

### Formatting conventions
- **Section headers in public channels**: bold + backtick (code-style) + emoji
  e.g. `:mag: *\`Why reconsider?\`*` or `:chart: *\`Observations\`*`
- **In-content emphasis**:
  - `_italic_` for softer focus / drawing attention to a key phrase
  - `*bold*` for strong emphasis on the most important part of a sentence
- **Plain headers in DMs**: no special formatting — just the label on its own line
- **Attribute / table / field names**: backtick code style `` `attribute_name` ``

### Recurring Vocabulary
- "Substantial" — for large or significant numbers
- "Implication:" — as a synthesis label after observations
- "Proposed solution" — for technical fix recommendations
- "WDYT?" — to invite input
- "Keep an eye out" — for upcoming results or follow-ups
- "Note:" — for important caveats or scope clarifications at the top

---

### Templates by Message Type

#### Decision / rollback announcement:
```
[Decision title]
@[relevant people]

[1-line decision statement]

Why [reconsider / decide]?
[Data point]: [number]. [Human implication].
[Data point]: [number]. [Human implication].

In summary, [conclusion restated].

Note: [nuance or forward-looking thought — we're not closing the door entirely].
```

#### Launch / A/B test announcement:
```
:rocket: [Feature name] [live / A/B-test live]
@[relevant people]

[What it is — 2 sentences].
[What it does for the customer — 1 sentence].

With this test, we aim to:
[Goal 1].
[Goal 2].

[Link to plan / deck]

[Closing hook with emoji — e.g. "Keep an eye out! :eyes:"]
```

#### Thread reply — stakeholder acknowledgment (short):
```
Thank you for the feedback, @[name]!

[Acknowledge the issue is on your radar].
[Honest reason if delayed]. [Specific commitment with timeline].
```

#### Thread reply — full structured answer:
```
@[stakeholders] cc @[others]

*Problem*
[1–2 sentence problem statement]

*Analysis*
[What was investigated, with whom, what was found]

*Proposed solution*
[What to do, why, trade-off acknowledged]

WDYT?
```

#### PR review request (Dutch DM):
```
Hey [naam]! Zou jij, wanneer je tijd hebt, deze PR kunnen reviewen?
:github: [PR title]
[1-sentence explanation of what the PR does]
```
For very small PRs:
```
Mag ik jou vragen voor een 1-line PR?
:github: [PR title]
```

#### Task update to mentee/close colleague (Dutch, progress format):
```
Hey [name]! Een update over de progress van [topic]:

[Feature/task name]
:checkmark-clean: [Completed item]
:checkmark-clean: [Completed item]
:to-do: [Remaining item]

[Free text follow-up if any context needed]
```

#### Question in a public/initiative channel (English, structured):
```
Hey all! / Hey @[group]! [1-line framing of what you need help with].

[Context section if needed — what you're trying to do, what works]
:checkmark-clean: [What is already clear/solved]
:question: [Where it gets unclear]

My question is:
[Clearly stated question — specific, 1–2 sentences]
[Optional: second sub-question]

[Details / example in thread :thread: / :github: PR link]
```

#### Technical deep-dive question to a close colleague (Dutch DM, structured):
```
Hey [name]! Zou je me kunnen helpen met een vraag over [topic]?

Context
[What you're investigating / the case you're working on]
[Link to case/thread if applicable]

Cause / Analysis / Deep dive
[What you found, step by step — specific table names, field names, join logic]
[Where the trail goes cold / what you expected vs. what happened]

Mijn vraag is:
[Clearly stated question]
[Why you expected different behaviour — frames the gap]
[Reference to more detail in thread if needed]
```

#### Analysis finding:
```
📊 *[Topic] Update*

*What we found:* [One sentence finding]
*Numbers:* [Key metric] → [Value] (vs. [comparison period/group])
*Why it matters:* [One sentence on business implication]
*Next step:* [Action or question]

[Link to full analysis]
cc @[relevant person if action needed]
```

#### A/B test result:
```
🧪 *A/B Test Result: [Test name / key_tag]*
Period: [start] – [end] ([N] days) | Market: [NL/DE/FR]

*Result: [✅ WIN / ➖ NO DIFFERENCE / 🔴 REGRESSION]*

[Primary metric]: [control value] → [treatment value] ([+/-X%], p=[p-value])

*Recommendation:* [Roll out / Iterate / Stop]
[Link to full analysis on Confluence]
```

#### Metric alert / concern:
```
⚠️ *[Metric] anomaly — [Market], [Period]*

[What happened in 1-2 sentences]
Possible causes: [bullets]
Next step: [who is investigating / what action]
```

### Confirmed unknowns / ask Maarten if
- Exact Slack channel names for specific initiatives (ask per task)
- Whether to write in Dutch or English if the audience is ambiguous
