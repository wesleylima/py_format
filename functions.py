from typing import Callable
import tiktoken

models = [
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-4",
    "gpt-4-32k",
]

# https://platform.openai.com/docs/models/overview
model_token_size = {
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
}

# https://openai.com/pricing
# 1/10000 of a dollar per 1000 tokens (input_token_cost_per_1000, output_token_cost_per_1000)
model_costs = {
    "gpt-3.5-turbo": (15, 20),
    "gpt-3.5-turbo-16k": (30, 40),
    "gpt-4": (300, 600),
    "gpt-4-32k": (600, 1200),
}

# How much bigger we expect the output to be than the input
EXPANSION_FACTOR = 1.2  # 20% larger


def find_models_that_fit_code(code: str, prompt_function: Callable):
    usable_models = {}

    # for all of our tasks, the out will always be at least the same size as the input
    for model in models:
        encoding = tiktoken.encoding_for_model(model)
        input_tokens = len(encoding.encode(prompt_function(code)))

        estimated_output_tokens = int(len(encoding.encode(code)) * EXPANSION_FACTOR)

        total_tokens = input_tokens + estimated_output_tokens
        if model_token_size[model] > total_tokens:
            usable_models[model] = (input_tokens, estimated_output_tokens)

    return usable_models


def get_best_model(code: str, prompt_function: Callable):
    """Find the cheapest model that will fit the input and output"""

    # Models that will fit the input and estimated output
    usable_models = find_models_that_fit_code(code, prompt_function)
    print("USABLE MODELS", usable_models)
    if not usable_models:
        print(
            "No models will fit the input and output. Use a strategy to split this file"
        )
        raise Exception("Code is too large")

    best_model = None

    # Now we optimize for cost
    for model, (input_tokens, output_tokens) in usable_models.items():
        input_cost_per_kilotoken = model_costs[model][0]
        output_cost_per_kilotoken = model_costs[model][1]

        model_cost = (
            (input_cost_per_kilotoken * input_tokens)
            + (output_cost_per_kilotoken * output_tokens)
        ) / (1000 * 10000)

        total_tokens = input_tokens + output_tokens

        if not best_model or best_model[1] > model_cost:
            best_model = (model, model_cost, output_tokens)

    print(
        f"The best model is {best_model[0]} and will cost ${best_model[1]:.6f} for the total of {best_model[2]} tokens"
    )

    best_model_name = best_model[0]

    total_tokens = (
        total_tokens
        if total_tokens < model_token_size[best_model_name]
        else model_token_size[best_model_name]
    )
    return (best_model_name, total_tokens)

