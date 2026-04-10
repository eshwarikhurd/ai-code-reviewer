import anthropic
from dotenv import load_dotenv

load_dotenv()

# Hardcoded snippet to test — a deliberately bad Python function
TEST_CODE = """
def get_user(id):
    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = " + id
    cursor.execute(query)
    return cursor.fetchone()
"""

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


def review_code(code: str) -> str:
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"Please review this code:\n\n```python\n{code}\n```"
            }
        ],
        system=SYSTEM_PROMPT
    )

    return message.content[0].text


if __name__ == "__main__":
    print("Sending code to Claude for review...\n")
    print("=" * 50)
    review = review_code(TEST_CODE)
    print(review)
    print("=" * 50)
    print("\nSuccess! API is working correctly.")