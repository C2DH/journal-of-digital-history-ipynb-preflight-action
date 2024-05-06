import requests
import fire
import json

### Example: python3 script.py *REPO_URL* *TOKEN* *NEW_REPO_NAME*
### Note: The token has to be a classic one with all permissions preferably.


def main_func(REPO_URL, PERSONAL_TOKEN, NEW_REPO_NAME):

    # REPO_URL = "https://github.com/jdh-observer/jYcpqGfdXPra"
    # PERSONAL_TOKEN = "token_here"
    # NEW_REPO_NAME = "jYcpqGfdXPra-fork"

    ### parsing the url

    splitted_url = REPO_URL.split("/")
    REPO_NAME = splitted_url[-1]
    REPO_OWNER = splitted_url[-2]

    print(f"Name - {REPO_NAME}, Owner - {REPO_OWNER}")

    github_session = requests.Session()
    _ = github_session.get(
        "https://github.com/repos/" + REPO_OWNER + "/" + REPO_NAME + "/forks"
    )

    ### forking the branch

    fork_request = github_session.post(
        "https://api.github.com/repos/" + REPO_OWNER + "/" + REPO_NAME + "/forks",
        headers={
            "Authorization": f"token {PERSONAL_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        json={
            "name": NEW_REPO_NAME,
            "default_branch_only": "true",
        },
    )

    print(f"Fork request http code - {fork_request.status_code}")

    ### getting username of the token's user

    token_user_info = github_session.get(
        "https://api.github.com/user",
        headers={
            "Authorization": f"token {PERSONAL_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
    )
    username = json.loads(token_user_info.text)
    USERNAME = username["login"]

    ### creating an issue

    issue_request = github_session.post(
        "https://api.github.com/repos/" + REPO_OWNER + "/" + REPO_NAME + "/issues",
        headers={
            "Authorization": f"token {PERSONAL_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={
            "title": f"Technical review on the https://github.com/{REPO_OWNER}/{REPO_NAME}",
            "body": f"https://github.com/{USERNAME}/{NEW_REPO_NAME}/blob/main/report.md",
            "assignees": ["eliselavy"],
        },
    )
    print(f"Issue creation http code - {issue_request.status_code}")

    print("done")


if __name__ == "__main__":
    fire.Fire(main_func)
