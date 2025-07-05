import requests
import yaml
import sys
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from IntelliReview.llm.base import LLMBase
from IntelliReview.llm.openai_wrapper import OpenAIWrapper

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
            diff_output = ""
            for file in files:
                filename = file["filename"]
                patch = file.get("patch", "")  # sometimes 'patch' may be missing
                diff_output += f"File: {filename}\n"
                diff_output += f"Changes:\n{patch}\n\n"
            return diff_output if diff_output.strip() else None
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
            matching_pr = None
            if input_pr_number:
                for pr in pull_requests:
                    if pr["number"] == input_pr_number:
                        matching_pr = pr
                        break
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

def generate_review_from_diff(llm: LLMBase, raw_pr_text: str):
    return llm.invoke({"diff": raw_pr_text})

if __name__ == "__main__":
    llm = OpenAIWrapper(api_key=OPEN_AI_KEY)
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
        if len(sys.argv) > 2:
            branch_name = sys.argv[2]
        latest_commit_contents = get_latest_commit_contents(branch_name)
        print(f"\nLatest Commit on this branch:\n {latest_commit_contents}")
        review = generate_review_from_diff(llm, latest_commit_contents)
        print("🔍 Review Comments:\n")
        print(review.content)
    else:
        sys.exit(f"Error: Unsupported argument '{sys.argv[1]}'. Only 'pull/commit' is allowed.")


