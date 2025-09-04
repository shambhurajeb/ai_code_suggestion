import os
import json
import openai
from github import Github

# Validate environment variables
required_env_vars = ["GITHUB_TOKEN", "OPENAI_API_KEY", "GITHUB_REPOSITORY", "GITHUB_EVENT_PATH"]
for var in required_env_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")

# Load tokens
github_token = os.getenv("GITHUB_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load GitHub event payload (contains PR number)
event_path = os.getenv("GITHUB_EVENT_PATH")
with open(event_path, "r") as f:
    event = json.load(f)

pr_number = event["pull_request"]["number"]
repo_name = os.getenv("GITHUB_REPOSITORY")

# Connect to GitHub
g = Github(github_token)
repo = g.get_repo(repo_name)

# Get PR details
pr = repo.get_pull(pr_number)
pr_title = pr.title
pr_body = pr.body or ""
files = pr.get_files()

# Collect file names for context
file_list = [file.filename for file in files]
file_summary = "\n".join(f"- {f}" for f in file_list) if file_list else "No files changed."

# Prepare prompt for a short review summary
prompt = f"""
You are a code reviewer. Provide a **short summary review** for the following pull request. 
Keep it concise, suitable for a GitHub comment.

PR Title: {pr_title}
PR Body: {pr_body}
Files Changed:
{file_summary}
"""

try:
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a senior code reviewer."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
    )
    review_summary = response.choices[0].message.content.strip()
    print(f"Review Summary:\n{review_summary}")

    # Post a single PR comment
    pr.create_issue_comment(f"### 🤖 AI PR Review Summary\n{review_summary}")

    # Save for GitHub summary output
    with open("review_summary.md", "w", encoding="utf-8") as f:
        f.write("## 🤖 AI PR Review Summary\n\n")
        f.write(review_summary)

except openai.APIError as e:
    print(f"⚠️ OpenAI API error: {e}")
    with open("review_summary.md", "w", encoding="utf-8") as f:
        f.write("⚠️ OpenAI API error. Could not generate PR review summary.")
except Exception as e:
    print(f"⚠️ Unexpected error: {e}")
    with open("review_summary.md", "w", encoding="utf-8") as f:
        f.write("⚠️ Unexpected error. Could not generate PR review summary.")
