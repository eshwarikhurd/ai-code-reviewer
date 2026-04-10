import os
import anthropic
from github import Github
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are an expert code reviewer. When given a code snippet, analyze it and provide structured feedback.

Format your response exactly like this:

## Code Review

### Critical Issues
- List any bugs, security vulnerabilities, or breaking problems

### Suggestions
- List improvements for readability, performance, or best practices

### Nitpicks
- Minor style or naming issues

### Summary
One sentence overall assessment.

Be specific and actionable. Reference line numbers or variable names where possible."""


def get_pr_diff(repo_name: str, pr_number: int) -> str:
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    diff_text = ""
    for file in pr.get_files():
        if file.filename.endswith((".py", ".js", ".ts", ".java", ".cpp", ".c")):
            if file.patch:
                added_lines = []
                for line in file.patch.split("\n"):
                    if line.startswith("+") and not line.startswith("+++"):
                        added_lines.append(line[1:])  # strip the leading +

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


if __name__ == "__main__":
    # Test: fetch diff from a real PR
    REPO = "eshwarikhurd/ai-code-reviewer"
    PR_NUMBER = 1  # we'll create this PR in a moment

    print(f"Fetching diff from PR #{PR_NUMBER}...")
    diff = get_pr_diff(REPO, PR_NUMBER)

    if not diff:
        print("No supported code files found in this PR.")
    else:
        print("Diff fetched successfully. Sending to Claude...\n")
        print("=" * 50)
        review = review_code(diff)
        print(review)
        print("=" * 50)