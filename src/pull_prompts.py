"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:

1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """Faz pull do prompt do LangSmith Prompt Hub."""

    username = os.getenv("USERNAME_LANGSMITH_HUB")

    if not username:
        raise ValueError("USERNAME_LANGSMITH_HUB não configurado no .env")

    prompt_name = "bug_to_user_story_v1"

    prompt = hub.pull(f"leonanluppi/{prompt_name}")

    output_path = Path("prompts") / f"{prompt_name}.yml"

    save_yaml(prompt, output_path)

    print(f"Prompt salvo em: {output_path}")


def main():
    """Função principal"""

    print_section_header("Pull do prompt ruim")

    check_env_vars([
    "LANGSMITH_API_KEY",
    ])

    pull_prompts_from_langsmith()

    return 0


if __name__ == "__main__":
    sys.exit(main())