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

## What all I used
- OpenAI API
- FastApi
- difflib
- Supabase
- Koyeb (Hosting)