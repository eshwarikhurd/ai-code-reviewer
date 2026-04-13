import os
import sys
import anthropic
from github import Github, Auth
from dotenv import load_dotenv

load_dotenv()

# ── PROMPT VARIANTS ──────────────────────────────────────────────────────────
# We'll test 4 prompts and compare results. Change ACTIVE_PROMPT to switch.

PROMPT_1_BASIC = """You are a code reviewer. Review the code and list any issues you find."""

PROMPT_2_STRUCTURED = """You are an expert code reviewer. When given a code snippet, analyze it and provide structured feedback.

Format your response exactly like this:

## Code Review

### Critical Issues
- List any bugs, security vulnerabilities, or breaking problems

### Suggestions
- List improvements for readability, performance, or best practices

### Nitpicks
- Minor style or naming issues

### Summary
One sentence overall assessment."""

PROMPT_3_SEVERITY = """You are a senior engineer doing a thorough code review. For each issue found, assign a severity:

🔴 CRITICAL — must fix before merge (bugs, security vulnerabilities, data loss risk)
🟡 SUGGESTION — should fix (performance, readability, best practices)
🔵 NITPICK — optional (style, naming, minor improvements)

Format your response as:

## Code Review

[severity emoji] **Issue title**
Problem: what is wrong
Fix: exactly how to fix it

End with a one-line summary and a MERGE DECISION: ✅ Approve / ⚠️ Approve with changes / ❌ Block."""

PROMPT_4_CONTEXTUAL = """You are a senior engineer reviewing a pull request. Think step by step:

1. First understand what the code is trying to do
2. Check for correctness — does it do what it intends?
3. Check for security — SQL injection, input validation, auth issues
4. Check for reliability — error handling, edge cases, resource leaks
5. Check for maintainability — naming, complexity, documentation

For each issue found, specify:
- Severity: CRITICAL / SUGGESTION / NITPICK
- Location: which function or line
- Problem: what is wrong and why it matters
- Fix: the exact corrected code where possible

End with: MERGE DECISION: Approve / Approve with changes / Block — and one sentence why."""

# ── CHANGE THIS TO SWITCH BETWEEN PROMPTS ────────────────────────────────────
ACTIVE_PROMPT = PROMPT_4_CONTEXTUAL
# ─────────────────────────────────────────────────────────────────────────────


def get_pr_diff(repo_name: str, pr_number: int) -> str:
    g = Github(auth=Auth.Token(os.getenv("GITHUB_TOKEN")))
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    diff_text = ""
    for file in pr.get_files():
        if file.filename.endswith((".py", ".js", ".ts", ".java", ".cpp", ".c")):
            if file.patch:
                added_lines = []
                for line in file.patch.split("\n"):
                    if line.startswith("+") and not line.startswith("+++"):
                        added_lines.append(line[1:])

                if added_lines:
                    diff_text += f"\n### File: {file.filename}\n"
                    diff_text += "\n".join(added_lines)

    return diff_text


def review_code(code: str, system_prompt: str) -> str:
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"Please review this code:\n\n```\n{code}\n```"
            }
        ],
        system=system_prompt
    )

    return message.content[0].text


if __name__ == "__main__":
    REPO = "eshwarikhurd/ai-code-reviewer"
    PR_NUMBER = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    print(f"Fetching diff from PR #{PR_NUMBER}...")
    diff = get_pr_diff(REPO, PR_NUMBER)

    if not diff:
        print("No supported code files found in this PR.")
    else:
        print(f"Running with ACTIVE_PROMPT...\n")
        print("=" * 50)
        review = review_code(diff, ACTIVE_PROMPT)
        print(review)
        print("=" * 50)