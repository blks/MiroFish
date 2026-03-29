"""
Translate CJK graph field text to English on read when the client locale is English.

Caches by graph_id + stable id + content hash to limit LLM cost.
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import re
from collections import OrderedDict
from typing import Any, Dict, List, Tuple

from ..config import Config
from .llm_client import LLMClient

logger = logging.getLogger(__name__)

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_CACHE: OrderedDict[str, str] = OrderedDict()
_CACHE_MAX = 512


def contains_cjk(text: str) -> bool:
    return bool(text and _CJK_RE.search(text))


def _cache_get(key: str) -> str | None:
    if key not in _CACHE:
        return None
    _CACHE.move_to_end(key)
    return _CACHE[key]


def _cache_set(key: str, value: str) -> None:
    _CACHE[key] = value
    _CACHE.move_to_end(key)
    while len(_CACHE) > _CACHE_MAX:
        _CACHE.popitem(last=False)


def _text_cache_key(graph_id: str, kind: str, stable_id: str, text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]
    return f"{graph_id}|{kind}|{stable_id}|{digest}"


def _chunk(lst: List[Any], size: int) -> List[List[Any]]:
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def _batch_translate(texts: List[str], client: LLMClient) -> List[str]:
    if not texts:
        return []
    payload = json.dumps({"strings": texts}, ensure_ascii=False)
    messages = [
        {
            "role": "system",
            "content": (
                "You translate knowledge-graph UI snippets to clear English. "
                'Return valid JSON only: {"translations": [...]} with the same number of '
                "strings as the input array, same order. Keep proper names and acronyms when sensible."
            ),
        },
        {"role": "user", "content": payload},
    ]
    try:
        out = client.chat_json(messages, temperature=0.2, max_tokens=min(4096, 120 * len(texts) + 128))
        arr = out.get("translations")
        if not isinstance(arr, list) or len(arr) != len(texts):
            logger.warning(
                "graph_text_i18n: translation length mismatch (expected %s)", len(texts)
            )
            return list(texts)
        merged: List[str] = []
        for raw, orig in zip(arr, texts):
            if raw is None or (isinstance(raw, str) and not raw.strip()):
                merged.append(orig)
            else:
                merged.append(str(raw))
        return merged
    except Exception as e:
        logger.warning("graph_text_i18n: batch translate failed: %s", e)
        return list(texts)


def maybe_localize_graph_data_for_request(
    graph_data: Dict[str, Any],
    graph_id: str,
    request_language: str,
) -> Dict[str, Any]:
    """
    When Accept-Language resolves to English, translate node summaries and edge facts
    that contain CJK characters. No-op if disabled, wrong locale, or LLM unavailable.
    """
    if request_language != "en":
        return graph_data
    if not Config.GRAPH_I18N_TRANSLATE_ON_READ:
        return graph_data
    if not Config.LLM_API_KEY:
        return graph_data

    try:
        client = LLMClient()
    except ValueError:
        return graph_data

    out = copy.deepcopy(graph_data)
    nodes = out.get("nodes") or []
    edges = out.get("edges") or []

    node_items: List[Tuple[int, str, str]] = []
    for i, n in enumerate(nodes):
        s = (n.get("summary") or "").strip()
        if s and contains_cjk(s):
            node_items.append((i, str(n.get("uuid") or i), s))

    for batch in _chunk(node_items, 12):
        pending: List[Tuple[int, str, str, str]] = []
        for idx, uuid, s in batch:
            ck = _text_cache_key(graph_id, "summary", uuid, s)
            hit = _cache_get(ck)
            if hit is not None:
                nodes[idx]["summary"] = hit
            else:
                pending.append((idx, uuid, s, ck))
        if not pending:
            continue
        texts = [p[2] for p in pending]
        translated = _batch_translate(texts, client)
        for (idx, _uuid, _s, ck), new_s in zip(pending, translated):
            _cache_set(ck, new_s)
            nodes[idx]["summary"] = new_s

    edge_items: List[Tuple[int, str, str]] = []
    for i, e in enumerate(edges):
        f = (e.get("fact") or "").strip()
        if f and contains_cjk(f):
            edge_items.append((i, str(e.get("uuid") or i), f))

    for batch in _chunk(edge_items, 12):
        pending = []
        for idx, uuid, f in batch:
            ck = _text_cache_key(graph_id, "fact", uuid, f)
            hit = _cache_get(ck)
            if hit is not None:
                edges[idx]["fact"] = hit
            else:
                pending.append((idx, uuid, f, ck))
        if not pending:
            continue
        texts = [p[2] for p in pending]
        translated = _batch_translate(texts, client)
        for (idx, _uuid, _f, ck), new_f in zip(pending, translated):
            _cache_set(ck, new_f)
            edges[idx]["fact"] = new_f

    return out
