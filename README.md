# tinygen

A simple Codegen.

## How to run
- Try running it using Postman.
- Use this url `https://testy-sheeree-tinygen-b060eaa8.koyeb.app/tinify` and select the `POST` method.
- Go to the `raw` tab and paste the following:
```
{
    "repoUrl": "https://github.com/jayhack/llm.sh",
    "prompt": "The program doesn't output anything in Windows 10"
}
```
- It should return a diff of the main file with the updated code.

## To run on your machine
- Install the python-venv package using `pip install python-venv`.
- Create a virtual-env called `tiny-venv` using `python -m venv tiny-venv`.
- Install the packages using `pip install -r requirements.txt`. 
- Start the server using `uvicorn app:app --host 0.0.0.0`.
- If `pip` and  `python` don't work, try using `pip3` and `python3`.
- To start the app in hot-reload mode, run `uvicorn app:app --reload`.

## What all I used
- OpenAI API
- FastApi
- difflib
- Supabase
- Koyeb (Hosting)