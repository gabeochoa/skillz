---
name: skill-evaluator
description: >
  A/B test whether a skill is worth loading for a specific task. Spawns two parallel
  Claude Code sessions — one with the skill injected as context, one without — and compares
  results to empirically determine if the skill actually helps. Use when the user asks
  "is skill X worth it for task Y?", "do I need the X skill?", "evaluate skill X",
  "skill A/B test", "test if skill helps", "is this skill useful for", "compare with
  and without skill", "skill evaluation", "skill-evaluator", "worth loading",
  "should I load skill X", or wants empirical evidence of whether a skill improves
  task completion quality.
---

# Skill Evaluator — A/B Testing for Skill Usefulness

Empirically test whether a specific skill improves the agent's ability to complete
a given task. Instead of guessing, run two parallel CC sessions and compare.

## Prerequisites

- A CLI node with `claude` installed (`which claude`)
- The skill must exist (in `SKILLS/` or the marketplace)

## Workflow

### Step 1: Parse the Request

Extract two things:
- **Skill slug:** e.g. `deploy-tool`, `db-migrations`
- **Task description:** What the user wants to accomplish

Example: "Is `deploy-tool` worth loading to ship a service?"
→ skill=`deploy-tool`, task="ship a service with the deploy tool"

If the user doesn't specify a task, ask them. The evaluation is meaningless without a
concrete task to test against.

### Step 2: Load the Skill Content

```bash
# Try local first
SKILL_CONTENT=$(cat SKILLS/<slug>/SKILL.md 2>/dev/null)

# Fallback: marketplace
if [ -z "$SKILL_CONTENT" ]; then
  bash SKILLS/skills/skills.sh get <slug>
fi
```

Capture the full SKILL.md content. If it has companion files (scripts, configs), note
them but focus on SKILL.md for the A/B test.

### Step 3: Create the Evaluation Prompts

Create two prompt files on the CLI node. Both prompts must be identical EXCEPT for the
skill context injection.

```bash
EVAL_DIR="/tmp/skill-eval-$(date +%s)"
mkdir -p "$EVAL_DIR"
```

**Prompt A (WITH skill) — write to `$EVAL_DIR/prompt_a.md`:**

```
You are being evaluated on your ability to complete a task. Be thorough and specific.
Your output will be compared against a baseline run without additional context.

## Reference Documentation (loaded for this evaluation)

<INSERT FULL SKILL.MD CONTENT HERE>

## Task

<INSERT TASK DESCRIPTION HERE>

## Output Format

Respond with a structured analysis:

1. APPROACH: Step-by-step how you would accomplish this task
2. COMMANDS: The exact commands, code, file paths, or actions you would run
3. PITFALLS: Common mistakes or gotchas you would avoid
4. CONFIDENCE: Rate 1-10 how confident you are in this approach
5. MISSING_INFO: What additional context would you need?
6. TOOLS_USED: What specific tools, CLIs, or APIs does your approach rely on?

Be specific. Show exact commands, file paths, and code snippets. No hand-waving.
```

**Prompt B (WITHOUT skill — baseline) — write to `$EVAL_DIR/prompt_b.md`:**

Same as above but WITHOUT the "Reference Documentation" section. The task description
and output format must be byte-for-byte identical.

### Step 4: Run Both Sessions in Parallel

Launch both CC sessions simultaneously. Use background execution since each can take
1-5 minutes.

```bash
# On the CLI node — run as a single background script
cat > "$EVAL_DIR/run_eval.sh" << 'EVALSCRIPT'
#!/bin/bash
EVAL_DIR="$1"

# Session A — WITH skill context
cd "${REPO_ROOT:-$HOME}"
claude -p "$(cat $EVAL_DIR/prompt_a.md)" --output-format=json --max-budget-usd 2   < /dev/null > "$EVAL_DIR/result_a.json" 2>"$EVAL_DIR/stderr_a.log" &
PID_A=$!

# Session B — WITHOUT skill (baseline)
claude -p "$(cat $EVAL_DIR/prompt_b.md)" --output-format=json --max-budget-usd 2   < /dev/null > "$EVAL_DIR/result_b.json" 2>"$EVAL_DIR/stderr_b.log" &
PID_B=$!

# Wait for both
wait $PID_A
EXIT_A=$?
wait $PID_B
EXIT_B=$?

echo "SESSION_A_EXIT=$EXIT_A"
echo "SESSION_B_EXIT=$EXIT_B"
echo "EVAL_COMPLETE"
EVALSCRIPT

chmod +x "$EVAL_DIR/run_eval.sh"
```

Run in the background:
```bash
bash "$EVAL_DIR/run_eval.sh" "$EVAL_DIR"
```

### Step 5: Extract and Compare Results

Read both result files:

```bash
# Extract the text result from JSON output
RESULT_A=$(cat "$EVAL_DIR/result_a.json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('result','ERROR'))")
RESULT_B=$(cat "$EVAL_DIR/result_b.json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('result','ERROR'))")

# Also extract cost
COST_A=$(cat "$EVAL_DIR/result_a.json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('cost_usd',0))")
COST_B=$(cat "$EVAL_DIR/result_b.json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('cost_usd',0))")
```

Evaluate across these dimensions:

| Dimension | Weight | What to Compare |
|-----------|--------|----------------|
| **Accuracy** | 30% | Correct commands, paths, APIs, tool names? |
| **Specificity** | 25% | References specific workflows/flags from the skill? |
| **Pitfall Awareness** | 20% | Catches gotchas the baseline misses? |
| **Completeness** | 15% | Covers more steps or edge cases? |
| **Hallucination** | 10% | Does the baseline invent incorrect commands? |

Score each dimension 1-10 for both sessions. Compute weighted totals.

### Step 6: Deliver the verdict

Present results as a summary card or short report with:

1. **Verdict:** WORTH IT / MARGINAL / NOT WORTH IT
2. **Scores:** With-skill vs baseline (weighted total out of 10)
3. **Key Differences:** Specific things the skill added (or didn't)
4. **Evidence:** Quote the most telling differences between outputs
5. **Cost:** How much each session cost
6. **Recommendation:** Always load / load for specific tasks / skip it

### Verdict Criteria

| Verdict | Score Delta | Meaning |
|---------|------------|---------|
| **WORTH IT** | ≥ 2.0 | Skill meaningfully improves output quality |
| **MARGINAL** | 0.5 – 1.9 | Skill helps a bit but CC mostly figures it out |
| **NOT WORTH IT** | < 0.5 | No meaningful difference or skill adds noise |

## Cost Control

- Default budget: $2 per session ($4 total for both)
- For complex tasks, allow up to $5 per session
- Always pass `--max-budget-usd` to prevent runaway costs
- Report actual cost in the verdict card

## Quick Mode (No CC Available)

If no CLI node with CC is connected, fall back to *theoretical evaluation*:

1. Read the skill content
2. Identify what unique knowledge it provides (org-specific commands, internal paths,
   gotchas, non-obvious workflows)
3. Assess: Is this knowledge commonly available, or would CC hallucinate without it?
4. Give a theoretical verdict with lower confidence

Flag clearly: "⚠️ Theoretical evaluation — no CC available for empirical A/B test"

## Edge Cases

| Situation | Handling |
|-----------|----------|
| Skill not found | Search marketplace, offer alternatives |
| CC not installed | Fall back to Quick Mode |
| Task too vague | Ask user to be more specific |
| Skill is huge (>8000 chars) | Truncate to most relevant sections, note in verdict |
| Both sessions fail | Report failure, suggest manual test |
| One session fails | Report partial result, re-run failed session once |
| Identical outputs | Verdict = NOT WORTH IT (skill added nothing) |

## Example Usage

User: "Is the `deploy-tool` skill worth loading if I want to debug a failing deploy?"

The agent:
1. Reads `SKILLS/deploy-tool/SKILL.md`
2. Creates prompts A (with skill) and B (without)
3. Runs both CC sessions in parallel on the CLI node
4. Compares: Session A used `deploy-tool status --job <name>`, Session B tried `kubectl get pods`
5. Delivers verdict: WORTH IT (+3.5 delta) — baseline hallucinated incorrect tooling
