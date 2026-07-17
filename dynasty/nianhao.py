# -*- coding: utf-8 -*-
"""年号语义主题链：候选打分、选号、改元策略。"""
from __future__ import annotations

import random
from typing import Iterable, Optional

from dynasty.nianhao_data import NIANHAO_BY_NAME, NIANHAO_ENTRIES, NIANHAO_NAMES

# 合成后备用字（库耗尽时）
_FALLBACK_CHARS = "建元平太开天宝大中盛和治熙庆兴宁隆顺应永康安泰定嘉景光德"

# 改元策略（混合制）
GAIYUAN_MIN_SEGMENT_YEARS = 2
GAIYUAN_BASE_CHANCE = 0.18
GAIYUAN_REPEAT_CHANCE = 0.08
GAIYUAN_MAX_SEGMENTS = 5
GAIYUAN_IMPACT_THRESHOLD = 5

REASON_ACCESSION = "accession"
REASON_REFRESH = "refresh"
REASON_GAIYUAN_GOOD = "gaiyuan_good"
REASON_GAIYUAN_BAD = "gaiyuan_bad"
REASON_GAIYUAN = "gaiyuan"


def entry_for(name: str) -> dict:
    if name in NIANHAO_BY_NAME:
        return NIANHAO_BY_NAME[name]
    themes = []
    for ch in name:
        if ch not in themes:
            themes.append(ch)
        if len(themes) >= 3:
            break
    return {"name": name, "themes": themes or ["元"], "tone": "neutral", "weight": 3}


def themes_of(name: str) -> list[str]:
    return list(entry_for(name).get("themes") or [])


def preferred_tones(reason: str) -> list[str]:
    if reason == REASON_GAIYUAN_BAD:
        return ["mitigate", "neutral", "auspicious"]
    if reason == REASON_GAIYUAN_GOOD:
        return ["auspicious", "neutral", "mitigate"]
    if reason in (REASON_ACCESSION, REASON_REFRESH, REASON_GAIYUAN):
        return ["auspicious", "neutral", "mitigate"]
    return ["neutral", "auspicious", "mitigate"]


def _theme_overlap(candidate_themes: Iterable[str], anchor_themes: Iterable[str]) -> int:
    anchor = set(anchor_themes or [])
    if not anchor:
        return 0
    return sum(1 for t in candidate_themes if t in anchor)


def score_candidate(entry: dict, reason: str, anchor_themes: Optional[list[str]] = None) -> float:
    score = float(entry.get("weight", 5))
    tone = entry.get("tone", "neutral")
    prefs = preferred_tones(reason)
    if tone in prefs:
        score += (3 - prefs.index(tone)) * 4
    else:
        score -= 2

    overlap = _theme_overlap(entry.get("themes") or [], anchor_themes or [])
    if anchor_themes:
        if overlap > 0:
            score += 12 * overlap
        else:
            # 同帝改元强烈偏好共享主题字；无共享则大幅降权
            if reason.startswith("gaiyuan"):
                score -= 18
            else:
                score -= 2
    return score


def _weighted_choice(scored: list[tuple[dict, float]]) -> str:
    weights = [max(0.01, s) for _, s in scored]
    total = sum(weights)
    r = random.random() * total
    acc = 0.0
    for (entry, _), w in zip(scored, weights):
        acc += w
        if r <= acc:
            return entry["name"]
    return scored[-1][0]["name"]


def generate_fallback_name(used: set[str], anchor_themes: Optional[list[str]] = None) -> str:
    """库耗尽时按主题字组合两字年号。"""
    used = set(used or [])
    anchors = list(anchor_themes or [])
    for _ in range(400):
        if anchors and random.random() < 0.75:
            a = random.choice(anchors)
            b = random.choice(_FALLBACK_CHARS)
            if b == a:
                b = random.choice([c for c in _FALLBACK_CHARS if c != a])
            candidate = a + b if random.random() < 0.55 else b + a
        else:
            candidate = random.choice(_FALLBACK_CHARS) + random.choice(_FALLBACK_CHARS)
        if len(candidate) == 2 and candidate[0] != candidate[1] and candidate not in used:
            return candidate
    suffix = 1
    while True:
        candidate = f"永安{suffix}"
        if candidate not in used:
            return candidate
        suffix += 1


def pick_nianhao(
    used: Iterable[str],
    reason: str = REASON_REFRESH,
    previous_name: Optional[str] = None,
    anchor_themes: Optional[list[str]] = None,
) -> str:
    """
    选取未用年号。
    - previous_name / anchor_themes：同帝主题链锚点
    - reason：accession / refresh / gaiyuan_good / gaiyuan_bad
    """
    used_set = set(used or [])
    themes = list(anchor_themes or [])
    if not themes and previous_name:
        themes = themes_of(previous_name)

    available = [e for e in NIANHAO_ENTRIES if e["name"] not in used_set]
    if not available:
        return generate_fallback_name(used_set, themes)

    scored: list[tuple[dict, float]] = []
    for entry in available:
        scored.append((entry, score_candidate(entry, reason, themes)))

    # 保留得分较高的一批再加权抽，避免永远只出最高分
    scored.sort(key=lambda x: x[1], reverse=True)
    cutoff = max(8, min(40, len(scored)))
    if len(scored) > cutoff:
        # 若主题链场景有共享主题的候选，优先在该子集内截断
        if themes and reason.startswith("gaiyuan"):
            themed = [x for x in scored if _theme_overlap(x[0].get("themes") or [], themes) > 0]
            if len(themed) >= 3:
                scored = themed[:cutoff]
            else:
                scored = scored[:cutoff]
        else:
            scored = scored[:cutoff]

    return _weighted_choice(scored)


def should_gaiyuan(
    dynasty_hp_change: float,
    segment_years: int,
    segment_count: int,
    rng: Optional[random.Random] = None,
) -> bool:
    """混合制：极端国运冲击 + 概率；一帝多数不改元，长寿者可多次。"""
    roll = (rng or random).random
    if abs(dynasty_hp_change) < GAIYUAN_IMPACT_THRESHOLD:
        return False
    if segment_years < GAIYUAN_MIN_SEGMENT_YEARS:
        return False
    if segment_count >= GAIYUAN_MAX_SEGMENTS:
        return False
    chance = GAIYUAN_BASE_CHANCE if segment_count <= 1 else GAIYUAN_REPEAT_CHANCE
    # 冲击越大略提高概率
    if abs(dynasty_hp_change) >= 7:
        chance += 0.08
    return roll() < chance


def gaiyuan_reason_from_impact(dynasty_hp_change: float) -> str:
    if dynasty_hp_change >= GAIYUAN_IMPACT_THRESHOLD:
        return REASON_GAIYUAN_GOOD
    if dynasty_hp_change <= -GAIYUAN_IMPACT_THRESHOLD:
        return REASON_GAIYUAN_BAD
    return REASON_GAIYUAN


def gaiyuan_event_text(old_name: str, new_name: str, dynasty_hp_change: float) -> str:
    if dynasty_hp_change <= -GAIYUAN_IMPACT_THRESHOLD:
        return f"灾异频仍，皇帝下诏改元，自 {old_name} 改为 {new_name}，以祈消弭。"
    if dynasty_hp_change >= GAIYUAN_IMPACT_THRESHOLD:
        return f"祥瑞叠至 / 武功告成，皇帝诏告天下，改元 {new_name}（自 {old_name}）。"
    return f"皇帝为应天象，改元 {new_name}。"


def register_nianhao(used: Iterable[str], name: str) -> list:
    """登记已用年号，返回 list 形式以兼容旧状态字段。"""
    result = list(used or [])
    if name and name not in result:
        result.append(name)
    return result


# 供外部兼容
__all__ = [
    "NIANHAO_NAMES",
    "NIANHAO_ENTRIES",
    "NIANHAO_BY_NAME",
    "pick_nianhao",
    "themes_of",
    "entry_for",
    "should_gaiyuan",
    "gaiyuan_reason_from_impact",
    "gaiyuan_event_text",
    "register_nianhao",
    "REASON_ACCESSION",
    "REASON_REFRESH",
    "REASON_GAIYUAN_GOOD",
    "REASON_GAIYUAN_BAD",
]
