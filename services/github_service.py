import requests
from urllib.parse import urlparse

def get_user_repo_from_github_url(github_url):
    parsed_url = urlparse(github_url)

    if parsed_url.netloc != 'github.com':
        return "Invalid GitHub URL"

    path_parts = parsed_url.path.strip('/').split('/')
    
    if len(path_parts) < 2:
        return "Invalid GitHub repository URL"

    user = path_parts[0]
    repo = path_parts[1]

    return user, repo


def fetch_file_content(file, user, repo):
    raw_url = f'https://raw.githubusercontent.com/{user}/{repo}/refs/heads/main/{file}'
    response = requests.get(raw_url)
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: Unable to fetch content, status code {response.status_code}"


def get_github_files(repo_url):
    parts = repo_url.rstrip('/').split('/')
    if len(parts) < 5 or parts[-3] != "github.com":
        return {"error": "Invalid GitHub repository URL."}

    owner, repo = parts[-2], parts[-1]

    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    response = requests.get(api_url)

    if response.status_code == 200:
        files = []
        contents = response.json()

        def fetch_files(contents):
            for item in contents:
                if item['type'] == 'file':
                    files.append(item['path'])
                elif item['type'] == 'dir':
                    dir_response = requests.get(item['url'])
                    if dir_response.status_code == 200:
                        fetch_files(dir_response.json())

        fetch_files(contents)

        return files
    else:
        return {"error": "Failed to fetch repository content. Make sure the repository is public and exists."}
