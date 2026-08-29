"""
Testes automatizados para validação de prompts.
"""

import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestPrompts:

    def setup_method(self):
        """Carrega o prompt otimizado antes de cada teste."""
        project_root = Path(__file__).parent.parent
        prompt_path = project_root / "prompts" / "bug_to_user_story_v2.yml"
        self.prompt = load_prompts(str(prompt_path))

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in self.prompt
        assert self.prompt["system_prompt"].strip() != ""

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona."""
        system_prompt = self.prompt["system_prompt"].lower()

        assert "você é" in system_prompt

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = self.prompt["system_prompt"].lower()

        assert "user story" in system_prompt

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída."""
        system_prompt = self.prompt["system_prompt"].lower()

        assert "exemplo 1" in system_prompt
        assert "relato de bug:" in system_prompt
        assert "saída:" in system_prompt

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum [TODO] no texto."""
        system_prompt = self.prompt["system_prompt"]

        assert "[TODO]" not in system_prompt
        assert "[todo]" not in system_prompt.lower()

    def test_minimum_techniques(self):
        """Verifica se pelo menos 2 técnicas foram listadas."""
        techniques = self.prompt.get("techniques_applied", [])

        assert len(techniques) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])