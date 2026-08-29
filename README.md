# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

Projeto do módulo de Prompt Engineering da pós-graduação em Engenharia de Software com IA. O objetivo foi puxar um prompt de baixa qualidade do LangSmith Prompt Hub, refatorá-lo com técnicas avançadas de Prompt Engineering, publicá-lo de volta e atingir >= 0.8 em todas as 5 métricas de avaliação (Helpfulness, Correctness, F1-Score, Clarity, Precision).

## Técnicas Aplicadas (Fase 2)

O prompt final (`prompts/bug_to_user_story_v2.yml`) combina três técnicas:

### 1. Role Prompting

**O quê:** o system prompt define uma persona clara — *"Product Manager / Business Analyst sênior, especialista em transformar relatos de bugs de qualquer tipo de produto (web, mobile, e-commerce, SaaS, ERP, CRM, backend/API) em User Stories"*.

**Por quê:** a primeira versão do prompt (ver seção "Resultados Finais") tinha um problema sutil de escopo — a persona era especializada demais em um único domínio, o que fazia o modelo forçar contexto de negócio irrelevante em bugs de outras áreas (e o dataset de avaliação cobre e-commerce, SaaS, mobile, ERP e CRM). Generalizar a persona para "qualquer produto de software", mas mantendo especificidade de PM/BA sênior, corrigiu isso sem perder qualidade na resposta.

**Exemplo prático:** no bug *"Botão de adicionar ao carrinho não funciona"*, o modelo assume persona de "cliente navegando na loja"; no bug *"Endpoint não valida permissões"*, assume "administrador do sistema" — a persona muda de acordo com o contexto de cada relato, não é fixa.

### 2. Few-shot Learning (obrigatório)

**O quê:** 4 exemplos completos de entrada/saída no próprio prompt, cobrindo padrões diferentes:
- Bug simples com **comparação implícita** entre plataformas (Safari vs Chrome) → mostra como transformar uma comparação em critérios de paridade/consistência mesmo sem estarem escritos literalmente
- Bug de sistema interno com **dado numérico preservado** (valor financeiro específico)
- Relato **vago** (edge case) → mostra como pedir esclarecimento em vez de inventar dados
- Bug técnico (falha de permissão) → mostra como incluir **requisitos técnicos observáveis** (códigos HTTP, auditoria) como critérios de aceite, sem cair em sugestão de código/arquitetura

**Por quê:** few-shot foi a técnica mais decisiva do projeto — não só pra formato (o modelo aprende a estrutura exata de "Como um X, eu quero Y, para que Z" + critérios "Dado/Quando/Então"), mas principalmente pra **calibrar o nível de detalhe esperado**. Isso resolveu diretamente o gargalo do F1-Score (ver Resultados Finais).

### 3. Chain of Thought (CoT)

**O quê:** o system prompt instrui o modelo a raciocinar internamente em 5 passos antes de escrever a resposta final (identificar persona/problema/comportamento esperado → identificar dados técnicos a preservar → listar consequências e requisitos técnicos observáveis implícitos → checar se falta informação → só então redigir), sem expor esse raciocínio na saída.

**Por quê:** relatos de bugs complexos (múltiplos problemas, causas técnicas específicas) exigem que o modelo processe várias dimensões do problema antes de escrever. Pedir esse raciocínio explícito — mas escondido da resposta final — reduziu alucinação (melhorou Correctness) e aumentou a cobertura de critérios de aceite relevantes (melhorou Recall/F1) sem sujar a Clarity da resposta final.

## Diagnóstico e Processo de Iteração

O processo não foi linear — documentando porque a jornada importa tanto quanto o resultado:

1. **v2.1** — primeira versão otimizada, mas com a persona especializada em um domínio específico (contas a pagar). Resultado: Correctness e F1-Score baixos, porque o modelo forçava contexto financeiro em bugs de e-commerce, SaaS e mobile que não tinham nada a ver com isso.
2. **v2.2** — generalizada a persona pra qualquer domínio e corrigido o template de saída para bater exatamente com o formato esperado pelo avaliador ("Como um X, eu quero Y, para que Z" + critérios Dado/Quando/Então). Todas as métricas passaram, exceto F1-Score.
3. **Diagnóstico do F1-Score** — usando um script de debug que expõe o `reasoning` do avaliador de F1 (que o `evaluate.py` calcula mas não imprime), identificamos que o prompt estava sendo conservador demais: por causa da regra "não inclua solução técnica", o modelo omitia requisitos técnicos que já estavam implícitos no relato (códigos HTTP esperados, requisitos de acessibilidade, valores-alvo de performance, necessidade de notificação ao usuário) — derrubando o Recall.
4. **v2.3** — regra de "não invente solução técnica" reescrita para distinguir claramente "sugerir tecnologia/arquitetura" (proibido) de "requisito técnico observável e testável" (obrigatório quando implícito no relato); removida a contagem fixa de critérios de aceite em favor de cobertura completa; adicionada regra para nunca confundir o valor atual do problema com o valor-alvo esperado. Resultado: todas as métricas >= 0.8.

## Resultados Finais

### Métricas — v2 (versão aprovada)

| Métrica | Nota | Status |
|---|---|---|
| Helpfulness | 0.89 | ✓ |
| Correctness | 0.84 | ✓ |
| F1-Score | 0.80 | ✓ |
| Clarity | 0.90 | ✓ |
| Precision | 0.88 | ✓ |
| **Média Geral** | **0.8611** | **✅ APROVADO** |

### Comparação: v1 (baixa qualidade) vs v2 (otimizado)

| Aspecto | v1 | v2 |
|---|---|---|
| Persona/Role | Nenhuma — "um assistente que ajuda a transformar relatos de bugs em tarefas para desenvolvedores" (genérico, sem especialidade) | Product Manager/BA sênior, adaptável a qualquer domínio |
| Few-shot examples | Nenhum | 4 exemplos cobrindo comparação implícita, dado preservado, edge case e requisito técnico |
| Chain of Thought | Nenhum — instrução direta de "analise o relato e crie uma user story", sem estrutura de raciocínio | 5 passos de raciocínio interno antes da resposta final |
| Formato de saída | Não especificado — apenas "User Story gerada:" no fim do prompt, sem estrutura, sem critérios de aceite exigidos | Estrutura fixa: User Story (Como/quero/para que) + Critérios de Aceitação (Dado/Quando/Então) |
| Tratamento de edge cases | Nenhum — nenhuma instrução para relatos vagos, dados conflitantes ou informações faltantes | Relatos vagos → pedido de esclarecimento; valores conflitantes → sinalização; requisitos técnicos implícitos → incluídos como critérios testáveis |
| Regras de comportamento | Nenhuma — apenas a instrução de análise, sem regras explícitas | 8 regras explícitas (não inventar dados, preservar valores concretos, distinguir requisito técnico observável de solução técnica, cobertura completa de critérios, não confundir valor atual com valor-alvo, etc.) |

### Evidências no LangSmith

- Dashboard/projeto: https://smith.langchain.com/projects/desafio_pos_graduacao [privado — acesso restrito à conta; ver traces públicas abaixo para avaliação sem login]
- Dataset de avaliação (15 exemplos): dataset `desafio_pos_graduacao-eval` em Datasets & Experiments no LangSmith
- Tracing detalhado (3 exemplos, links públicos, sem necessidade de login):
  - https://smith.langchain.com/public/24c1db70-9a34-4576-8cfa-a2c800123b69/r/92ab788a-afa3-4ca0-963b-98d21d40671e
  - https://smith.langchain.com/public/1dc2398a-56ae-4df5-9361-d6c67dc01d49/r/95fbde04-aeea-4f9a-bc9d-412efcbed185
  - https://smith.langchain.com/public/13a54931-f51b-4993-9945-049f03988957/r/98ba108b-f5eb-4a16-afcd-80d6cec80527
- Screenshots do resultado final da avaliação (terminal, `python src/evaluate.py`, todas as métricas >= 0.8): ver pasta `evidencias/` [PREENCHER se aplicável]

## Como Executar

### Pré-requisitos

- Python 3.9+
- Conta no [LangSmith](https://smith.langchain.com) com API Key
- API Key da OpenAI (usada neste projeto) — [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### 1. Configuração inicial

```bash
git clone https://github.com/nataliapedrosas/mba-ia-pull-evaluation-prompt.git
cd mba-ia-pull-evaluation-prompt

python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Copie `.env.example` para `.env` e preencha:

```
LANGSMITH_API_KEY=sua_chave_aqui
USERNAME_LANGSMITH_HUB=seu_username
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EVAL_MODEL=gpt-4o
OPENAI_API_KEY=sua_chave_aqui
```

### 2. Pull do prompt inicial (baixa qualidade)

```bash
python src/pull_prompts.py
```

Isso salva o prompt ruim localmente em `prompts/bug_to_user_story_v1.yml`.

### 3. Push do prompt otimizado

O prompt otimizado já está em `prompts/bug_to_user_story_v2.yml`. Para publicá-lo no LangSmith Hub:

```bash
python src/push_prompts.py
```

### 4. Avaliação

```bash
python src/evaluate.py
```

O script roda o prompt contra os 15 exemplos do dataset, calcula as 5 métricas e exibe o resultado no terminal. Critério de aprovação: todas as métricas individuais >= 0.8 **e** média geral >= 0.8.

### 5. (Opcional) Debug de métricas específicas

Caso alguma métrica fique abaixo de 0.8, `src/debug_evaluate.py` imprime, para cada exemplo do dataset, a resposta gerada, a reference esperada e o `reasoning` do avaliador — útil para identificar exatamente o que está sendo omitido ou incluído indevidamente:

```bash
python src/debug_evaluate.py
```

### 6. Testes de validação

```bash
pytest tests/test_prompts.py
```
