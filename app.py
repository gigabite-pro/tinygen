from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.command_request import CommandRequest
from services.github_service import get_user_repo_from_github_url, get_github_files, fetch_file_content
from services.openai_service import send_openAI_request
from services.supabase_service import save_to_supabase
import json
import difflib

app = FastAPI()

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

    save_to_supabase(repo_url, prompt, diff)

    return diff
