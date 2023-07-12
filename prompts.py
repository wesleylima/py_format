def create_conversion_prompt(code: str) -> str:
    prompt = f"""
        I have the following Python code file:

        ----------------------------------------
        ${code}
        ----------------------------------------

        I would like you to convert this code to working TypeScript and write detailed documentation and type annotations for it. Make variable and function names more clear and easier to understand.  Do NOT change the underlying code logic itself, only convert it to TypeScript and add the documentation and type annotations.

        Respond ONLY with the Python code file with the documentation added, and nothing else. Do not respond with any other text.
        """
    return prompt


def create_typehint_prompt(code: str) -> str:
    prompt = f"""
        I have the following Python code file:

        ----------------------------------------
        {code}
        ----------------------------------------

        I would like you to convert this code to working Python with type hints and write detailed documentation. Avoid using the "any" type. If the type is unclear, make a best guess.

        Respond ONLY with the Python code file with the type hints added, and nothing else. Do not respond with any other text.
        """
    return prompt
