import aiohttp
import asyncio
from dotenv import load_dotenv
import os
import argparse
import aiofiles
from prompts import create_typehint_prompt
from functions import get_best_model

load_dotenv()


async def queryGPT(query: str, apiKey: str, model: str, max_tokens: int) -> str:
    """
    * Sends a query to OpenAI API endpoint to get a response with generated code
    * @param query The prompt string to be sent to OpenAI API
    * @param apiKey The API key to access GPT
    * @returns A Promise with a string response containing the generated code
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + apiKey,
            },
            json={
                "model": model,
                # "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": query}],
            },
        ) as response:
            data: dict = await response.json()

            try:
                updatedCode: str = data["choices"][0]["message"]["content"]
                return updatedCode
            except Exception as e:
                print("Error processing OpenAI API response:", data)
                print(e)
                raise Exception("Failed to process OpenAI API response")


async def main() -> None:
    API_KEY = os.getenv("OPEN_API_KEY")
    parser = argparse.ArgumentParser(description="format a python file")
    parser.add_argument(
        "filename", nargs="?", type=str, help="The filname that we want to format"
    )
    parser.add_argument(
        "--typehint", action="store_true", help="Adds typehints to the specified file"
    )
    args = parser.parse_args()

    if not args.filename:
        print("No file to format")
        return

    async with aiofiles.open(args.filename, mode="r") as f:
        code = await f.read()

    if args.typehint:
        print("lets format some code!")
        model, max_tokens = get_best_model(code, create_typehint_prompt)
        print(f"Using {model}")
        print(f"Will have a total of {max_tokens} tokens")
        query: str = create_typehint_prompt(code)

        formatted = await queryGPT(query, API_KEY, model, max_tokens)
        print(formatted)

    else:
        print("No action specified")


asyncio.run(main())
