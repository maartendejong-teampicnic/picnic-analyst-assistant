# Skill: Create PR (picnic-dbt-models)

## What this covers
Creating, reviewing, and merging pull requests in the `PicnicSupermarket/picnic-dbt-models`
repository. Covers branch naming, JIRA ticket creation, linting, CI checks, and review request workflow.

## When to use
When building or modifying edge models, reporting models, or any SQL/YAML/MD files in
`picnic-dbt-models`. All changes go through a PR — no direct pushes to master.

## How to do it

### PR Creation Workflow (step by step)

1. **Create JIRA ticket** via REST API → get CE-XXXX number (see JIRA section below)
2. **Create branch**: `git fetch origin master && git checkout -b maartendejong-teampicnic/CE-XXXX origin/master`
   - Default branch is **master** (not main)
   - Run from `~/Documents/Github/picnic-dbt-models/edge-models/`
3. **Write/modify** `.sql`, `.yml`, `.md` files (see `dbt-model-design.md` for SQL/YAML/MD templates)
4. **Validate models** (via docker exec — see Dev Container section):
   - `poetry run dbt run -s model_name --full-refresh` → output at `temp.maartenlex_<model_name>`
   - Ask Maarten to verify output in Snowflake before continuing
5. **Run `poetry run guide fix lint`** via docker exec — takes 3-5+ min; auto-reformats unrelated Python files with black
   - Exit code 0 = clean. Any reformatted files will appear in `git diff` — stage them too.
6. **Run dbt-score**: `poetry run dbt parse && poetry run dbt-score lint -s model_name` via docker exec → target 10/10
7. **Stage specific files only**: `git add <file>` — never `git add .`
8. **Commit**: `CE-XXXX picnic-dbt-models: [description]`
9. **Push and open PR**:
   ```
   git push -u origin maartendejong-teampicnic/CE-XXXX
   gh pr create --repo PicnicSupermarket/picnic-dbt-models --title "..." --body "..."
   ```
10. **Fill checklist** after model runs locally
11. **Wait for CI** — poll `gh pr checks <PR_NUMBER> --repo PicnicSupermarket/picnic-dbt-models` every 2 minutes until all checks pass.
12. **Draft reviewer Slack message** — once all checks are green (see Slack DM template below)

### Dev Container Architecture

- All `dbt` commands run inside the VS Code dev container (dbt 1.10.18), NOT the WSL host (dbt 1.9.6 — broken deps).
- Maarten opens VS Code via `code .` from WSL, accepts "Reopen in Dev Container" prompt, Rancher Desktop must be running.
- **Container name changes on each rebuild** — find it with: `docker ps --format "{{.Names}}" | grep vsc-edge`
- **Snowflake SSO**: auth triggers on first `dbt run` and opens a browser tab.

```bash
# Find container name
docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}" | grep -v k8s | grep -v pause

# Run model
docker exec <container_name> bash -c "cd /workspaces/picnic-dbt-models/edge-models && poetry run dbt run -s <model_name> --full-refresh 2>&1"

# Run dbt-score (run dbt parse first if model files changed)
docker exec <container_name> bash -c "cd /workspaces/picnic-dbt-models/edge-models && poetry run dbt parse && poetry run dbt-score lint -s <model_name> 2>&1"

# Run guide fix lint
docker exec <container_name> bash -c "cd /workspaces/picnic-dbt-models/edge-models && poetry run guide fix lint 2>&1"
```

Notes:
- `dbt-score lint` takes only ONE model at a time
- Always run `dbt parse` before dbt-score if model files were recently changed (manifest may be stale)

---

## Reference: Conventions & Patterns

### Repo details
- **Repo**: `PicnicSupermarket/picnic-dbt-models`
- **GitHub login**: `maartendejong-teampicnic`
- **Base branch**: `master`
- **Local path**: `~/Documents/Github/picnic-dbt-models/edge-models/`

### Branch naming — STRICT
**Always**: `maartendejong-teampicnic/CE-XXXX` — exactly this format, no title suffix.
- The `/create-git-branch` skill reads DEV_TABLE_PREFIX from `.env` (`maartenlex`) — **ignore it**, always use `maartendejong-teampicnic/CE-XXXX`

### PR title and body template
**PR title**: `CE-XXXX picnic-dbt-models: [short description of change]`

**PR body**:
```
Type: fix  (allowed: opt, feat, fix, brk, stable — validated by Danger bot)
Ticket: https://picnic.atlassian.net/browse/CE-XXXX

[Description of what changed and why]

### Checklist

- [ ] Model runs 🏃🏼
- [ ] Tests pass 🧪
- [ ] dbt-score is 10 🥇
- [ ] `guide fix lint` runs 🧪
```

### Editing PRs
- `gh pr edit` **fails silently** due to GraphQL deprecation error — use REST API instead:
  ```bash
  gh api repos/PicnicSupermarket/picnic-dbt-models/pulls/<PR_NUMBER> -X PATCH -f body='...'
  ```

### CI Checks on PRs
Five checks run on every PR:
- **CodeRabbit** — AI-powered PR review (leaves inline comments)
- **claude_review** — GitHub Actions job (~54s)
- **Monorepo PR Merge Gatekeeper (picnic-dbt-models)** — TeamCity build; **required** to merge
  - Build type ID: `AnalystDevelopmentPlatform_PicnicDbtModels_MonorepoPrMergeGatekeeperBuild`
  - Can lag significantly before appearing ("Waiting for status to be reported")
  - Check via `check-teamcity-build` skill with `refs/pull/<PR_NUMBER>/head`
  - PR is not complete until this passes
- **PR Checks (picnic-dbt-models)** — TeamCity build; runs Python/lint checks
- **danger/picnic-dbt-models (Python)** — validates PR description format; only re-triggers on push (not on description edits); use `git commit --allow-empty` + push to re-trigger if needed

Gatekeeper typically takes ~12 minutes to complete.

### JIRA Ticket Creation

```bash
curl -s -X POST \
  -u "maarten.dejong@teampicnic.com:<CONFLUENCE_API_TOKEN>" \
  -H "Content-Type: application/json" \
  "https://picnic.atlassian.net/rest/api/3/issue" \
  -d '{
    "fields": {
      "project": {"key": "CE"},
      "summary": "CE-XXXX description of ticket",
      "issuetype": {"id": "10665"},
      "assignee": {"accountId": "712020:196e3020-52d8-42b0-acbe-ce341308b4cd"},
      "description": {
        "type": "doc", "version": 1,
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Description here."}]}]
      }
    }
  }'
```

Key IDs:
- Project: `CE` (id: 11204)
- Issue type Task: `10665`
- Maarten's account ID: `712020:196e3020-52d8-42b0-acbe-ce341308b4cd`
- Board: https://picnic.atlassian.net/jira/software/projects/CE/boards/202
- Response contains `key` (e.g. `CE-2962`) — use as branch/PR identifier

### PR Review Request (Dutch DM, after all CI checks pass)
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
Draft the Slack DM immediately after pushing — don't wait for CI. Send only after Maarten approves.
Ask who the reviewer is if not already specified.

Reviewer varies per PR — **confirm reviewer with Maarten before opening the PR**.
