import os
import json
import openai
from github import Github

# Validate environment variables
required_env_vars = ["GITHUB_TOKEN", "OPENAI_API_KEY", "GITHUB_REPOSITORY", "GITHUB_EVENT_PATH"]
for var in required_env_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")

# Load GitHub tokens
github_token = os.getenv("GITHUB_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")
repo_name = os.getenv("GITHUB_REPOSITORY")

# Load GitHub event payload
with open(os.getenv("GITHUB_EVENT_PATH")) as f:
    event = json.load(f)

pr_number = event["pull_request"]["number"]

# Connect to GitHub
g = Github(github_token)
pr = g.get_repo(repo_name).get_pull(pr_number)

# Collect PHP check outputs from files if available
def load_output(name):
    path = f".github/check_outputs/{name}.txt"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return f"{name} output not available"

checks_summary = {
    "PHPCS": load_output("phpcs"),
    "PHPCBF": load_output("phpcbf"),
    "PHPStan": load_output("phpstan"),
    "Rector": load_output("rector"),
    "Composer Audit": load_output("composer_audit"),
}

prompt = f"""
You are a senior PHP reviewer. A PR has run the following quality checks:
{json.dumps(checks_summary, indent=2)}

Provide a concise review of the PR, highlighting:
- Coding standard issues
- Static analysis warnings
- Rector suggestions
- Security or dependency concerns from Composer audit
Do not change any files. Only provide review comments and suggestions in markdown format.
"""

try:
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a senior PHP code reviewer."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1200,
    )
    review = response.choices[0].message.content.strip()
    pr.create_issue_comment(f"## 🤖 AI PR Review\n\n{review}")
    print("✅ AI PR review posted successfully")
except Exception as e:
    print("⚠️ Failed to generate AI PR review:", e)
