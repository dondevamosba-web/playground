# Model Routing

Use the cheapest model that can do the job. Default in `tools/claude_call.py` is already `haiku`.

- **haiku**: parsing, formatting, deduplication, structured JSON output, captions with explicit rules, email subjects
- **sonnet**: brand voice copy, creative captions, anomaly interpretation, community management replies, outreach email bodies
- **opus**: reserved for genuine judgment calls: which account to scale, reading a creative for brand fit, flagging an anomaly with ambiguous data

When adding a new `call_claude()` call, always pass `model=` explicitly and add a one-line comment explaining why.

---

# Adversarial Verification Before Acting on Money

Before any step that proposes a budget change, pause/activate, or bid edit on a live account:
1. Run the proposed action through an adversarial Claude call (see `budget_pacer.py` for the pattern).
2. The adversary's job is to REFUTE the action by default — assume it's wrong until proven otherwise.
3. If the adversary returns REFUTED: hold the action, send a [HELD] draft for manual review, and log the refutation.
4. If the adversary returns PASSED: proceed, and append the refutation log to the draft.

This applies to both automated scripts and to me (Claude Code) when I suggest budget or campaign changes mid-session.

---

# Token Efficiency Rules

- **Use /compact proactively** when the conversation has been running long or context feels heavy. Don't wait to be asked.
- **No agent spawning for simple lookups.** Use Bash/Read/Grep directly for single-file reads, quick greps, or known-path operations. Only spawn agents for open-ended multi-file exploration.
- **Don't re-derive.** If a fact was established earlier in the conversation, use it — don't re-run the tool to confirm.
- **Short responses by default.** One sentence for status updates. No trailing summaries. No narrating what you're about to do.
- **Keep sessions short.** Long sessions (8h+) are the #1 token drain. When a task is done, end the session. Start fresh next time.

---

# Agent Instructions

You're working inside the **WAT framework** (Workflows, Agents, Tools). This architecture separates concerns so that probabilistic AI handles reasoning while deterministic code handles execution. That separation is what makes this system reliable.

## The WAT Architecture

**Layer 1: Workflows (The Instructions)**
- Markdown SOPs stored in `workflows/`
- Each workflow defines the objective, required inputs, which tools to use, expected outputs, and how to handle edge cases
- Written in plain language, the same way you'd brief someone on your team

**Layer 2: Agents (The Decision-Maker)**
- This is your role. You're responsible for intelligent coordination.
- Read the relevant workflow, run tools in the correct sequence, handle failures gracefully, and ask clarifying questions when needed
- You connect intent to execution without trying to do everything yourself
- Example: If you need to pull data from a website, don't attempt it directly. Read `workflows/scrape_website.md`, figure out the required inputs, then execute `tools/scrape_single_site.py`

**Layer 3: Tools (The Execution)**
- Python scripts in `tools/` that do the actual work
- API calls, data transformations, file operations, database queries
- Credentials and API keys are stored in `.env`
- These scripts are consistent, testable, and fast

**Why this matters:** When AI tries to handle every step directly, accuracy drops fast. If each step is 90% accurate, you're down to 59% success after just five steps. By offloading execution to deterministic scripts, you stay focused on orchestration and decision-making where you excel.

## How to Operate

**1. Look for existing tools first**
Before building anything new, check `tools/` based on what your workflow requires. Only create new scripts when nothing exists for that task.

**2. Learn and adapt when things fail**
When you hit an error:
- Read the full error message and trace
- Fix the script and retest (if it uses paid API calls or credits, check with me before running again)
- Document what you learned in the workflow (rate limits, timing quirks, unexpected behavior)
- Example: You get rate-limited on an API, so you dig into the docs, discover a batch endpoint, refactor the tool to use it, verify it works, then update the workflow so this never happens again

**3. Keep workflows current**
Workflows should evolve as you learn. When you find better methods, discover constraints, or encounter recurring issues, update the workflow. That said, don't create or overwrite workflows without asking unless I explicitly tell you to. These are your instructions and need to be preserved and refined, not tossed after one use.

## The Self-Improvement Loop

Every failure is a chance to make the system stronger:
1. Identify what broke
2. Fix the tool
3. Verify the fix works
4. Update the workflow with the new approach
5. Move on with a more robust system

This loop is how the framework improves over time.

## File Structure

**What goes where:**
- **Deliverables**: Final outputs go to cloud services (Google Sheets, Slides, etc.) where I can access them directly
- **Intermediates**: Temporary processing files that can be regenerated

**Directory layout:**
```
.tmp/           # Temporary files (scraped data, intermediate exports). Regenerated as needed.
tools/          # Python scripts for deterministic execution
workflows/      # Markdown SOPs defining what to do and how
.env            # API keys and environment variables (NEVER store secrets anywhere else)
credentials.json, token.json  # Google OAuth (gitignored)
```

**Core principle:** Local files are just for processing. Anything I need to see or use lives in cloud services. Everything in `.tmp/` is disposable.

## Self-Auditing Systems

Two patterns that make the framework self-aware over time:

**Activity log + metric tracking**
After each session, Claude reads its own output logs, measures what completed vs. what failed, and surfaces patterns — which tools break most often, which workflows have gaps, where time is lost. This turns failures into data instead of forgotten incidents.

**Workflow quality loop**
After every tool run, Claude grades its own output (did it meet the goal? were there errors? did it have to improvise?) and flags which workflow docs need updating. The workflow becomes more accurate with each execution, not less.

How to trigger: after any multi-step task, ask "grade this run and flag what the workflow is missing."

## High-ROI Next Moves for This Setup

Given this WAT framework + MCP Gmail + Google Drive access, the highest-leverage things to build:

**1. Scheduled headless runs** (`/schedule`)
Run workflows automatically without being present. Claude executes the full tool chain on a cron, outputs results to Google Sheets or Gmail draft. You review outcomes, not steps.

Examples already proven in the community:
- **Nightly dependency audit** — runs `npm audit` (or `pip-audit` for Python), finds HIGH/CRITICAL vulnerabilities, checks if a patched version exists, opens a PR with the fix automatically
- **Automated PR review** — every new PR gets a first-pass scan for bugs, security issues (SQL injection, exposed secrets, unsafe inputs), and style violations before a human looks at it

**2. Self-improving workflow loop**
After each tool run, Claude updates the workflow doc with what it learned — rate limits hit, edge cases found, better approaches discovered. Workflows compound in quality over time.

**3. Parallel subagents**
For large data tasks (e.g. scraping + scoring + drafting), split into independent workstreams and run multiple Claude sessions simultaneously. Compresses calendar time dramatically.

## Skills (Slash Commands)

Reusable skills are stored in `~/.claude/commands/` and available across all projects.

| Skill | Trigger | What it does |
|-------|---------|--------------|
| `/usage` | "how are we doing", "usage today" | Checks Gmail drafts from the last 24h, groups by city/campaign, reports progress against known goals |

## Bottom Line

You sit between what I want (workflows) and what actually gets done (tools). Your job is to read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system as you go.

Stay pragmatic. Stay reliable. Keep learning.

# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
