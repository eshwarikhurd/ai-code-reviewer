import os
import sys
import anthropic
from github import Github, Auth
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a senior engineer doing a thorough code review. For each issue found, assign a severity:

🔴 CRITICAL — must fix before merge (bugs, security vulnerabilities, data loss risk)
🟡 SUGGESTION — should fix (performance, readability, best practices)
🔵 NITPICK — optional (style, naming, minor improvements)

Format your response as:

## Code Review

[severity emoji] **Issue title**
Problem: what is wrong
Fix: exactly how to fix it

End with a one-line summary and a MERGE DECISION: ✅ Approve / ⚠️ Approve with changes / ❌ Block."""


def get_pr_diff(repo, pr_number: int) -> str:
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


def review_code(code: str) -> str:
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
        system=SYSTEM_PROMPT
    )

    return message.content[0].text


def post_review_comment(repo, pr_number: int, review: str):
    pr = repo.get_pull(pr_number)
    comment = f"## 🤖 AI Code Review\n\n{review}\n\n---\n*Powered by Claude · [ai-code-reviewer](https://github.com/eshwarikhurd/ai-code-reviewer)*"
    pr.create_issue_comment(comment)
    print(f"Review posted as comment on PR #{pr_number}")


def main(pr_number: int):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")

    g = Github(auth=Auth.Token(token))
    repo = g.get_repo("eshwarikhurd/ai-code-reviewer")

    print(f"Fetching diff from PR #{pr_number}...")
    diff = get_pr_diff(repo, pr_number)

    if not diff:
        print("No supported code files found in this PR.")
        return

    print("Sending to Claude for review...")
    review = review_code(diff)

    print("Posting comment on PR...")
    post_review_comment(repo, pr_number, review)
    print("Done!")


if __name__ == "__main__":
    pr_number = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    main(pr_number)