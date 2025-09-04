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
files = pr.get_files()

comments = []
quota_exceeded = False

# Function to split large patch into chunks
def split_into_chunks(text, chunk_size=2000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# Analyze each file change
for file in files:
    print(f"Processing file: {file.filename}")
    patch = file.patch or ""
    
    if not patch:
        continue

    # Split patch if too large
    patch_chunks = split_into_chunks(patch, chunk_size=3000)

    suggestions = []
    for idx, chunk in enumerate(patch_chunks):
        prompt = f"""
        You are a code reviewer. Suggest improvements for the following code:

        Filename: {file.filename}
        Patch (chunk {idx+1}/{len(patch_chunks)}):
        {chunk}
        """

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a senior code reviewer."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1200,  # increased to allow full feedback
            )
            suggestion = response.choices[0].message.content.strip()
            suggestions.append(suggestion)
        except openai.APIError as e:
            if "insufficient_quota" in str(e):
                print(f"⚠️ OpenAI quota exceeded while analyzing `{file.filename}`")
                quota_exceeded = True
                break
            else:
                print(f"⚠️ OpenAI API error analyzing `{file.filename}`: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error analyzing `{file.filename}`: {e}")

    # Append combined suggestions for the file
    if suggestions:
        comments.append(f"### 💡 Suggestions for `{file.filename}`\n" + "\n\n".join(suggestions))

# Show results in GitHub Checks output
if comments:
    body = "\n\n".join(comments)

    # Post a single PR comment
    try:
        pr.create_issue_comment(body)
    except Exception as e:
        print(f"⚠️ Failed to post PR comment: {e}")

    # Save suggestions for GitHub summary
    with open("suggestions.md", "w", encoding="utf-8") as f:
        f.write("## 🤖 AI Code Suggestions\n\n")
        f.write(body)
elif quota_exceeded:
    with open("suggestions.md", "w", encoding="utf-8") as f:
        f.write("⚠️ OpenAI quota exceeded. Could not analyze all files.")
else:
    with open("suggestions.md", "w", encoding="utf-8") as f:
        f.write("✅ No AI suggestions. Your code looks good!")
