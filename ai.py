import json
import logging
import re
import time
import unicodedata
import os
import requests

from config import CAREER_LABELS

logger = logging.getLogger(__name__)

# Configurações da API da IA / AI API settings
AI_API_KEY = os.environ.get("AI_API_KEY", os.environ.get("ANTHROPIC_API_KEY", os.environ.get("GROQ_API_KEY", os.environ.get("OPENAI_API_KEY", ""))))
AI_MODEL = "claude-haiku-4-5"
AI_URL = "https://api.anthropic.com/v1/messages"

# Instruções de comportamento da IA / AI behavior instructions
PROMPT_RELEVANCE = """Você é o filtro de um portal de notícias de concursos públicos voltado para bacharéis em Direito que buscam oportunidades de carreira jurídica.

O objetivo do portal é alertar o usuário quando surge uma oportunidade nova ou quando algo muda de forma relevante para quem está decidindo se inscrever, estudar ou acompanhar um certame específico.

Com esse objetivo em mente, avalie se o conteúdo abaixo vale ser exibido para esse público. Pergunte-se: um bacharel em Direito acompanhando concursos acharia relevante?

Se for relevante, identifique também a CARREIRA do certame, escolhendo UMA das opções:
"tribunais"; se Juiz, Analista ou Técnico de Tribunais de Justiça, TRF, TRE, TRT, STJ, STF, TSE, TST, Tribunal de Contas (TC) não entra aqui
"mp"; se Promotor de Justiça, Analista ou Técnico do Ministério Público
"defensoria"; se Defensor Público, Analista ou Técnico da Defensoria
"procuradorias"; se Procurador Legislativo, de Estado ou Município, Federal, da Fazenda Nacional, ou Advogado da União ou de entidades ou órgãos públicos
"policiais"; se Delegado de Polícia ou carreiras policiais estritamente jurídicas
"administrativo"; se cargos jurídicos de menor importância em orgãos públicos, Prefeituras, Conselhos, Autarquias ou Empresas Públicas, etc
"estagio"; se Residência Jurídica ou Estágio de Pós-graduação em Direito

Se for relevante, identifique também GROUP no formato "orgao-localidade-cargo" usando apenas letras minúsculas, números e hífens, SEM acentos
Exemplos
"cgm-porto_velho_ro-auditor"
"prefeitura-martinopolis_sp-advogado"
"sefaz-ce-auditor_fiscal"
"pgm-caxias_do_sul_rs-procurador"
"al-ms-analista_juridico"
"tj-to-residencia_juridica"

Responda APENAS no seguinte formato JSON, sem nenhum texto adicional:
{"relevant": true, "reason": "Em um resumo de ~500 caracteres, descreva o cargo e o contexto específico do certame sem usar frases como \"relevante para bacharéis em Direito\", \"exige formação em Direito\" ou similares, essas conclusões são óbvias; agregue informação, não reafirme o óbvio", "career": "...escolha uma das opções...", "group": "orgao-localidade-cargo"}
ou
{"relevant": false, "reason": "Irrelevante"}

Conteúdo para avaliar:
"""

PROMPT_CONSOLIDATION = """Abaixo está uma lista JSON de notícias sobre concursos, cada uma com um 'id', 'title', 'reason' e um 'group' (identificador provisório).
Sua tarefa é identificar quais notícias falam do mesmo certame/concurso e unificar o campo 'group'.
Se duas ou mais notícias falam de um mesmo orgão, provavelmente são do mesmo certame, analise com cuidado, o 'group' delas deve ser idêntico (repita um dos identificadores já existentes ou crie um novo padronizado).
Responda APENAS com um objeto JSON válido, onde as chaves são as strings dos IDs originais e os valores são as strings do novo 'group' unificado.
Exemplo: Se o ID "1" e "3" falam do TJSP para Juiz, e o ID "2" fala do MPSP, responda:
{"1": "tjsp-juiz", "3": "tjsp-juiz", "2": "mpsp-promotor"}

Lista de itens:
"""

def normalize_group(g: str) -> str:
    """Normaliza o nome do grupo gerado por IA (remove acentos e espaços) / Normalizes the AI-generated group name (removes accents and spaces)"""
    if not g:
        return ""
    g = unicodedata.normalize("NFKD", g).encode("ascii", "ignore").decode("ascii")
    g = g.lower().strip()
    g = re.sub(r"[^a-z0-9-]", "-", g)
    g = re.sub(r"-+", "-", g).strip("-")
    return g

def call_ai_api(system_prompt: str, user_content: str) -> str:
    """Faz a chamada HTTP para a API da IA com lógica de repetição / Makes the HTTP call to the AI API with retry logic"""
    payload = {
        "model": AI_MODEL,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_content}
        ],
        "max_tokens": 2048,
    }
    for attempt in range(3):
        try:
            resp = requests.post(
                AI_URL,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": AI_API_KEY,
                    "anthropic-version": "2023-06-01",
                },
                json=payload,
                timeout=45,
            )
            resp.raise_for_status()
            data = resp.json()
            content_list = data.get("content", [])
            content = content_list[0].get("text") if content_list else ""
            finish_reason = data.get("stop_reason", "unknown")
            if not content:
                logger.warning("API da IA retornou conteúdo vazio (stop_reason=%s) na tentativa %d/3", finish_reason, attempt + 1)
                if attempt < 2:
                    time.sleep(10 * (attempt + 1))
                continue
            return content.strip()
        except requests.exceptions.HTTPError as e:
            body = ""
            try:
                body = e.response.text[:500]
            except Exception:
                pass
            logger.error("API da IA tentativa %d/3 falhou [HTTP %s]: %s | body: %s", attempt + 1, e.response.status_code if e.response is not None else "?", e, body)
            if attempt < 2:
                time.sleep(10 * (attempt + 1))
        except Exception as e:
            logger.error("API da IA tentativa %d/3 falhou: %s", attempt + 1, e)
            if attempt < 2:
                time.sleep(10 * (attempt + 1))
    return ""

def _validate_evaluation(data) -> dict:
    """Valida e normaliza a resposta da IA contra um schema esperado / Validates and normalizes the AI response against an expected schema"""
    if not isinstance(data, dict):
        return {"relevant": False, "reason": "response not a json object"}

    relevant = data.get("relevant")
    if not isinstance(relevant, bool):
        return {"relevant": False, "reason": "missing or invalid 'relevant' field"}

    reason_raw = data.get("reason", "")
    reason = reason_raw if isinstance(reason_raw, str) else str(reason_raw or "")

    result = {"relevant": relevant, "reason": reason}

    if relevant:
        career_raw = data.get("career", "")
        career = career_raw.strip().lower() if isinstance(career_raw, str) else ""
        result["career"] = career if career in CAREER_LABELS else "administrativo"

        group_raw = data.get("group", "")
        result["group"] = normalize_group(group_raw if isinstance(group_raw, str) else "")

    return result


def evaluate_relevance(url: str, title: str, text: str) -> dict:
    """Envia o conteúdo da página para a IA e retorna uma avaliação validada / Sends page content to the AI and returns a validated evaluation"""
    if not AI_API_KEY:
        return {"relevant": False, "reason": "AI_API_KEY not configured"}
    if not text or len(text) < 50:
        return {"relevant": False, "reason": "insufficient text"}

    content = f"URL: {url}\nTítulo: {title}\n\nTexto:\n{text}"
    response = call_ai_api(PROMPT_RELEVANCE, content)

    if not response:
        return {"relevant": False, "reason": "empty response from AI"}

    try:
        raw = json.loads(response)
    except json.JSONDecodeError:
        return {"relevant": False, "reason": "error parsing response", "raw_response": response}

    result = _validate_evaluation(raw)
    result["raw_response"] = response
    return result


def consolidate_groups(relevant_items: list) -> None:
    """Faz um passe de consolidação para unificar os identificadores de grupo de itens que tratam do mesmo certame / Consolidation pass to unify group IDs of items about the same exam"""
    if not AI_API_KEY or len(relevant_items) <= 1:
        return

    items_to_send = [
        {
            "id": str(i),
            "title": item.get("real_title") or item.get("title") or "",
            "reason": item.get("reason", ""),
            "group": item.get("group", "")
        }
        for i, item in enumerate(relevant_items)
    ]

    content = json.dumps(items_to_send, ensure_ascii=False, indent=2)
    response = call_ai_api(PROMPT_CONSOLIDATION, content)

    if not response:
        logger.warning("Falha na consolidação de grupos: sem resposta da IA.")
        return

    try:
        mapping = json.loads(response)
        if isinstance(mapping, dict):
            for i, item in enumerate(relevant_items):
                str_i = str(i)
                if str_i in mapping:
                    item["group"] = normalize_group(mapping[str_i])
    except json.JSONDecodeError:
        logger.warning("Falha na consolidação de grupos: resposta não é JSON.")
    except Exception as e:
        logger.warning("Falha na consolidação de grupos: %s", e)
