import requests
import yaml
import sys

with open("secrets.yml", "r") as file:
    secrets = yaml.safe_load(file)
GITHUB_TOKEN = secrets["GITHUB_TOKEN"]

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

def get_latest_pull_request():
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/pulls?sort=created&direction=desc"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        pull_requests = response.json()
        if pull_requests:
            latest_pr = pull_requests[0]  # Get the most recent pull request
            pr_url = latest_pr["url"]
            pr_response = requests.get(pr_url, headers=headers)
            if pr_response.status_code == 200:
                pr_details = pr_response.json()
                print(f"Latest PR #{latest_pr['number']}: {latest_pr['title']} by {latest_pr['user']['login']}")
                print(f"Description: {pr_details['body']}\n")

                # Fetch and parse the diff file to get changed files and their diffs
                diff_url = latest_pr["diff_url"]
                diff_response = requests.get(diff_url, headers=headers)
                if diff_response.status_code == 200:
                    print(diff_response.text)
                else:
                    print(f"Failed to fetch diff file: {diff_response.status_code}")
                return pr_details
            else:
                print(f"Failed to fetch details for PR #{latest_pr['number']}: {pr_response.status_code}")
                return None
        else:
            print("No pull requests found.")
            return None
    else:
        print(f"Failed to fetch pull requests: {response.status_code}")
        return None

if __name__ == "__main__":
    branch_name = "main"
    if len(sys.argv) > 2:
        branch_name = sys.argv[2]
    
    if sys.argv[1] == "commit":
        latest_commit_contents = get_latest_commit_contents(branch_name)

    if sys.argv[1] == "pull" or len(sys.argv) <= 2: 
        latest_pull_request = get_latest_pull_request()
        if latest_pull_request:
            print("\nLatest Pull Request:")
