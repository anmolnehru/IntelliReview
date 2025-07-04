import requests
import yaml
import sys
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

with open("secrets.yml", "r") as file:
    secrets = yaml.safe_load(file)
GITHUB_TOKEN = secrets["GITHUB_TOKEN"]
OPEN_AI_KEY = secrets["OPENAI_API_KEY"]

GITHUB_API_URL = "https://api.github.com"

REPO_OWNER = "anmolnehru"
REPO_NAME = "IntelliReview"

def get_latest_commit_contents(branch="main"):
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/commits?sha={branch}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        commits = response.json()
        latest_commit = commits[0]  # Get the most recent commit
        commit_url = latest_commit["url"]

        # Fetch the details of the latest commit
        commit_response = requests.get(commit_url, headers=headers)
        if commit_response.status_code == 200:
            commit_details = commit_response.json()
            files = commit_details.get("files", [])
            for file in files:
                print(f"File: {file['filename']}")
                print(f"Changes: {file['patch']}")
            return commit_details
        else:
            print(f"Failed to fetch commit details: {commit_response.status_code}")
            return None
    else:
        print(f"Failed to fetch commits: {response.status_code}")
        return None

def get_pull_requests_with_details():
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        pull_requests = response.json()
        for pr in pull_requests:
            pr_url = pr["url"]
            pr_response = requests.get(pr_url, headers=headers)
            if pr_response.status_code == 200:
                pr_details = pr_response.json()
                for file in pr_details.get("files", []):
                    print(f"- {file['filename']}")
                    print(f"Changes: {file['patch']}")

            else:
                print(f"Failed to fetch details for PR #{pr['number']}: {pr_response.status_code}")
        return pull_requests
    else:
        print(f"Failed to fetch pull requests: {response.status_code}")
        return None

def get_latest_pull_request(input_pr_number=None):
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/pulls?sort=created&direction=desc"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        pull_requests = response.json()
        if pull_requests:
            if input_pr_number:
                matching_pr = next((pr for pr in pull_requests if pr.get("number") == input_pr_number), None)
            else:
                matching_pr = pull_requests[0]  # Get the most recent pull request
            if not matching_pr:
                print(f"No pull request found with number {input_pr_number}.")
            pr_url = matching_pr["url"]
            pr_response = requests.get(pr_url, headers=headers)
            if pr_response.status_code == 200:
                pr_details = pr_response.json()
                print(f"Latest PR #{matching_pr['number']}: {matching_pr['title']} by {matching_pr['user']['login']}")
                print(f"Description: {pr_details['body']}\n")

                # Fetch and parse the diff file to get changed files and their diffs
                diff_url = matching_pr["diff_url"]
                diff_response = requests.get(diff_url, headers=headers)
                if diff_response.status_code == 200:
                    return diff_response.text
                else:
                    print(f"Failed to fetch diff file: {diff_response.status_code}")
            else:
                print(f"Failed to fetch details for PR #{matching_pr['number']}: {pr_response.status_code}")
        else:
            print("No pull requests found.")
    else:
        print(f"Failed to fetch pull requests: {response.status_code}")
    return None

def generate_review_from_diff(llm_input, raw_pr_text):
    """
    Given an LLM and raw pull request text (with diff and metadata),
    extract the unified diff and return LLM-generated review comments.

    Args:
        llm_input: A LangChain-compatible LLM instance (e.g., ChatOpenAI)
        raw_pr_text: Raw PR content (including diff)

    Returns:
        str: LLM-generated review comments
    """
    prompt = PromptTemplate.from_template("""
You are a very experienced software engineer performing a thorough code review on the following GitHub pull request diff:

{diff}

Please provide detailed, constructive review comments including:
- Potential bugs or logical errors
- Code style and formatting issues
- Best practices violations
- Suggestions for improving readability, performance, or security
- Anything unusual or risky

Do NOT just say 'No issues found' unless the code is absolutely perfect.
    """)

    chain = prompt | llm_input
    return chain.invoke({"diff": raw_pr_text})

if __name__ == "__main__":
    llm = ChatOpenAI(
        openai_api_key=OPEN_AI_KEY,
        model_name="gpt-4o",
        temperature=0.3
    )
    # get latest pull-request by default if no params
    if len(sys.argv) < 2 or sys.argv[1] == "pull":
        pr_number_input = input("Enter the PR number you want to fetch: ").strip()
        if pr_number_input == "":
            pr_number = None
        elif pr_number_input.isdigit():
            pr_number = int(pr_number_input)
        else:
            print("Invalid PR number.")
            sys.exit()
        matching_pull_request = get_latest_pull_request(pr_number)
        if matching_pull_request:
            print(f"\nLatest Pull Request:\n {matching_pull_request}")
            review = generate_review_from_diff(llm, matching_pull_request)
            print("🔍 Review Comments:\n")
            print(review.content)
        sys.exit()

    branch_name = "main"
    if sys.argv[1] == "commit":
        latest_commit_contents = get_latest_commit_contents(branch_name)
        if len(sys.argv) > 2:
            branch_name = sys.argv[2]
    else:
        sys.exit(f"Error: Unsupported argument '{sys.argv[1]}'. Only 'pull/commit' is allowed.")


