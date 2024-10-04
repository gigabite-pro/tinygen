from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
from fastapi.middleware.cors import CORSMiddleware
import requests
from openai import OpenAI
import json
import os
from urllib.parse import urlparse
import difflib
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

client = OpenAI(
    api_key = OPEN_AI_KEY
)

app = FastAPI()

class CommandRequest(BaseModel):
    repoUrl: str
    prompt: str

allowed_origins = ["*"]

app.add_middleware(CORSMiddleware, allow_origins=allowed_origins,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def read_root():
    return {"message": "Working"}

@app.post("/tinify")
def tinify(command: CommandRequest):
    repo_url = command.repoUrl
    prompt = command.prompt

    # Get all file names from the repo
    github_files = get_github_files(repo_url)

    # Get the file that is most important
    required_files = send_openAI_request(prompt, optional_text=f'Which 1 of these files do you think would be most important to solve this issue (usually would be a python file): {json.dumps(github_files)} Return as a json with "file_name" as the key and should have only 1 value that should be the name from the given array. Do not give as a code snippet.')

    # Get the username and repo name from the url to create a raw url
    user , repo = get_user_repo_from_github_url(repo_url)

    # Store the file name
    file_name = json.loads(required_files)["file_name"]
    print(file_name)

    # Get file content from github
    file_content = fetch_file_content(file_name, user, repo)

    # Get code improvements
    gpt_suggestion = send_openAI_request(prompt, optional_text=f'Modify this file (only if it solves the problem) to solve the problem. Only return the new code snippet (if nothing should be changed, return the original file content): {file_content}')
    
    # Ask if it wants to correct it's answer
    want_to_reflect = send_openAI_request(prompt="Are you sure about this or do you want to correct your answer? (answer with a 1 or 0 and not include a full stop.)")

    if int(want_to_reflect):
        gpt_suggestion = send_openAI_request(prompt, optional_text=f'Modify this file (only if it solves the problem) to solve the problem. Only return the new code snippet (if nothing should be changed, return the original file content): {file_content}')
    
    gpt_suggestion = gpt_suggestion[9:-3]
    
    diff = '\n'.join(difflib.unified_diff(file_content.splitlines(keepends=True), gpt_suggestion.splitlines(keepends=True), lineterm=''))

    response = (
    supabase.table("tinygen")
    .insert({"repo_url": repo_url, "prompt": prompt, "diff": diff})
    .execute()
    )

    return diff

def get_user_repo_from_github_url(github_url):
    # Parse the GitHub URL
    parsed_url = urlparse(github_url)

    # Check if the URL is from GitHub
    if parsed_url.netloc != 'github.com':
        return "Invalid GitHub URL"

    # Split the path to extract user and repo
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

def send_openAI_request(prompt="", optional_text=""):
    # print(optional_text)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f'{prompt}. {optional_text}'},
        ],
        store=True
    )

    return completion.choices[0].message.content

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
