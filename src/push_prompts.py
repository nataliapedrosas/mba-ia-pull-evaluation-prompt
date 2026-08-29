"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub.
    """

    try:
        system_prompt = prompt_data["system_prompt"]

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{bug_report}")
        ])

        full_prompt_name = f"{os.getenv('USERNAME_LANGSMITH_HUB')}/{prompt_name}"

        hub.push(
            full_prompt_name,
            object=prompt,
            new_repo_is_public=True
        )

        print(f"Prompt enviado com sucesso: {full_prompt_name}")
        return True

    except Exception as e:
        print(f"Erro ao fazer push do prompt: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt.
    """

    errors = []

    required_fields = [
        "description",
        "system_prompt",
        "version",
        "techniques_applied"
    ]

    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")

    if not prompt_data.get("system_prompt", "").strip():
        errors.append("system_prompt está vazio")

    techniques = prompt_data.get("techniques_applied", [])

    if len(techniques) < 2:
        errors.append(
            f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}"
        )

    return (len(errors) == 0, errors)


def main():
    """Função principal"""

    print_section_header("Push do prompt otimizado")

    if not check_env_vars([
        "LANGSMITH_API_KEY",
        "USERNAME_LANGSMITH_HUB"
    ]):
        return 1

    prompt_path = "prompts/bug_to_user_story_v2.yml"

    prompt_data = load_yaml(prompt_path)

    if prompt_data is None:
        return 1

    is_valid, errors = validate_prompt(prompt_data)

    if not is_valid:
        print("Prompt inválido:")
        for error in errors:
            print(f"  - {error}")
        return 1

    success = push_prompt_to_langsmith(
        "bug_to_user_story_v2",
        prompt_data
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())