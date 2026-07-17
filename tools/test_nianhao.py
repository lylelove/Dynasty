# -*- coding: utf-8 -*-
"""年号主题链与改元策略冒烟测试（无 GUI）。"""
from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dynasty import nianhao as nh
from dynasty.nianhao_data import NIANHAO_NAMES


def test_pool_size():
    assert len(NIANHAO_NAMES) >= 350, len(NIANHAO_NAMES)
    assert len(set(NIANHAO_NAMES)) == len(NIANHAO_NAMES)


def test_unique_and_diverse():
    used = []
    names = []
    for _ in range(80):
        n = nh.pick_nianhao(used, reason=nh.REASON_ACCESSION)
        assert n not in used
        used.append(n)
        names.append(n)
    assert len(set(names)) == 80


def test_theme_chain_on_gaiyuan():
    random.seed(42)
    hits = 0
    trials = 40
    for i in range(trials):
        used = []
        first = nh.pick_nianhao(used, reason=nh.REASON_ACCESSION)
        used.append(first)
        themes = nh.themes_of(first)
        second = nh.pick_nianhao(
            used,
            reason=nh.REASON_GAIYUAN_BAD if i % 2 else nh.REASON_GAIYUAN_GOOD,
            previous_name=first,
            anchor_themes=themes,
        )
        used.append(second)
        overlap = set(nh.themes_of(second)) & set(themes)
        if overlap:
            hits += 1
    # 主题链应明显优于纯随机（纯随机约 10–25%）
    rate = hits / trials
    assert rate >= 0.55, f"theme link rate too low: {rate:.2f} ({hits}/{trials})"


def test_should_gaiyuan_guards():
    assert nh.should_gaiyuan(5, 1, 1, rng=random.Random(0)) is False  # 段太短
    assert nh.should_gaiyuan(3, 5, 1, rng=random.Random(0)) is False  # 冲击不够
    assert nh.should_gaiyuan(5, 5, 5, rng=random.Random(0)) is False  # 段数上限
    # 满足条件时有一定概率为 True
    true_count = sum(
        1 for s in range(200) if nh.should_gaiyuan(6, 5, 1, rng=random.Random(s))
    )
    assert 10 < true_count < 120, true_count


def test_fallback_when_exhausted():
    used = list(NIANHAO_NAMES)
    name = nh.pick_nianhao(used, reason=nh.REASON_REFRESH)
    assert name
    assert name not in used


if __name__ == "__main__":
    test_pool_size()
    test_unique_and_diverse()
    test_theme_chain_on_gaiyuan()
    test_should_gaiyuan_guards()
    test_fallback_when_exhausted()
    print(f"OK: pool={len(NIANHAO_NAMES)}, theme-chain & policy checks passed")
