# -*- coding: utf-8 -*-
"""根据整局模拟结果，一键生成「让 AI 撰写完整国史」的提示词。"""


class HistoryPromptMixin:
    """汇总本局朝代、历代帝王、纪事与国运轨迹，拼装成可复制的国史写作提示词。"""

    # 每位皇帝编年保留的「关键节点」上限（改元与硬事件优先）
    _PROMPT_EVENTS_PER_REIGN = 8
    # 帝数超过此值时，中间诸帝纪事再压缩
    _PROMPT_FULL_DETAIL_EMP_MAX = 15
    # 宗藩世家小节最多列出的封国数
    _PROMPT_FIEFS_MAX = 10
    # 单个封国最多列出的历代国主数（超出则首尾节略）
    _PROMPT_FIEF_HOLDERS_MAX = 8
    # 宰辅小节最多列出的历任首辅数（超出则中段节略）
    _PROMPT_SHOUFU_MAX = 12

    def _describe_emperor_kinship(self, prev_emp, cur_emp):
        """描述当代皇帝与上一代皇帝的父系亲属关系，供国史行文交代世系承继。"""
        if prev_emp is None:
            return "开国之君，肇基立业"
        prev_p = self.get_person_by_id(prev_emp.get("pid")) if prev_emp.get("pid") else None
        cur_p = self.get_person_by_id(cur_emp.get("pid")) if cur_emp.get("pid") else None
        if prev_p is None or cur_p is None:
            return "承继前代（世系不详）"
        relation = self.describe_kinship(cur_p, prev_p)
        return f"为前代（{self._emp_display_name(prev_emp)}）之{relation}"

    def _ability_label(self, ab):
        """治国手腕改为定性措辞；数值钳制在 1–9。"""
        try:
            n = int(ab)
        except (TypeError, ValueError):
            n = 5
        n = max(1, min(9, n))
        if n >= 8:
            return "明察"
        if n >= 6:
            return "干练"
        if n >= 4:
            return "中人"
        return "昏庸"

    def _format_child_title(self, child):
        """子嗣封号：嗣位者标「嗣位，是为某宗」，其余用谥号/封号。

        返回值会被外层再包一层括号（见 _format_emperor_children），故此处内部
        不再自带括号，避免出现「（嗣位（是为某宗））」式嵌套。
        """
        if child.miaohao:
            return f"嗣位，是为{child.miaohao}"
        if child.shihao:
            return child.shihao
        if child.title and child.title not in ("", "皇帝"):
            return child.title
        if child.has_title and child.title_name:
            return self.format_enfeoffed_title(child.title_name, child.title_rank)
        if child.title_name:
            return self.format_enfeoffed_title(child.title_name, child.title_rank)
        if child.title == "太子" or child.is_heir:
            return child.title or "太子"
        return "无封"

    def _format_emperor_children(self, emp):
        """汇总某帝男系子嗣及各自封号，供国史本纪交代皇子分封。"""
        person = self.get_person_by_id(emp.get("pid")) if emp.get("pid") else None
        if person is None or not person.children:
            return "无"
        parts = []
        for cid in person.children:
            child = self.get_person_by_id(cid)
            if child is None or child.gender != "M":
                continue
            title = self._format_child_title(child)
            parts.append(f"{child.name}（{title}）")
        return "、".join(parts) if parts else "无"

    def _founder_name(self):
        """开局姓名：优先开局快照，其次 listjson 首帝，避免用末帝当前名。"""
        name = getattr(self, "founder_name", None) or ""
        if name:
            return name
        if self.listjson:
            return self.listjson[0].get("name") or "（未知）"
        return self.emperor or "（未知）"

    def _founder_nianhao(self):
        nh = getattr(self, "founder_nianhao", None) or ""
        if nh:
            return nh
        if self.listjson:
            hist = self.listjson[0].get("nianhao_history") or []
            if hist:
                return hist[0].get("nianhao") or "（未知）"
            summary = self.listjson[0].get("nianhao") or ""
            if summary:
                # 「贞观3年、延平23年」→ 取首段年号名
                first = summary.split("、")[0]
                for i, ch in enumerate(first):
                    if ch.isdigit():
                        return first[:i] or first
                return first.replace("年", "") or "（未知）"
        return self.yearNumber or "（未知）"

    def _emp_display_name(self, emp):
        """本纪与国运统一用「庙号·姓名」或姓名。"""
        name = emp.get("name") or ""
        miaohao = emp.get("miaohao") or ""
        if miaohao and miaohao not in ("（无庙号）",):
            return f"{miaohao}·{name}" if name else miaohao
        return name or "（佚名）"

    def _reign_fortune_line(self, emp):
        """国运起峰谷终，一律整数（用途说明统一放在写作约束里，不逐行重复）。"""
        def _i(key, alt=None):
            v = emp.get(key)
            if v is None and alt is not None:
                v = alt
            try:
                return int(round(float(v)))
            except (TypeError, ValueError):
                return None

        start = _i("dynasty_hp_start")
        end = _i("dynasty_hp_end")
        peak = _i("dynasty_hp_peak", start)
        trough = _i("dynasty_hp_trough", end)
        if start is None and end is None:
            return None
        start = start if start is not None else 0
        end = end if end is not None else 0
        peak = peak if peak is not None else max(start, end)
        trough = trough if trough is not None else min(start, end)
        return f"国运 {start}→峰{peak}/谷{trough}→终{end}"

    def _is_gaiyuan_event(self, text):
        return bool(text) and ("改元" in text)

    def _compress_reign_events(self, events, limit=None):
        """
        同一帝在位期间的事件压缩：
        - 改元全文保留；
        - 同文案合并为「……（凡 N 见）」；
        - 总数截断至 limit，优先改元与首次出现的异类事件。
        """
        limit = limit if limit is not None else self._PROMPT_EVENTS_PER_REIGN
        if not events:
            return []

        # 保持时间顺序，合并相同 event 文案
        ordered = []  # [{time, event, count, is_gaiyuan}]
        index_by_text = {}
        for ev in events:
            text = (ev.get("event") or "").strip()
            if not text or text == "今年无事发生。":
                continue
            time_str = ev.get("time") or ""
            if self._is_gaiyuan_event(text):
                ordered.append({
                    "time": time_str,
                    "event": text,
                    "count": 1,
                    "is_gaiyuan": True,
                })
                continue
            if text in index_by_text:
                ordered[index_by_text[text]]["count"] += 1
            else:
                index_by_text[text] = len(ordered)
                ordered.append({
                    "time": time_str,
                    "event": text,
                    "count": 1,
                    "is_gaiyuan": False,
                })

        if len(ordered) <= limit:
            selected = ordered
        else:
            # 先取全部改元，再按出现顺序补满
            gaiyuan = [x for x in ordered if x["is_gaiyuan"]]
            others = [x for x in ordered if not x["is_gaiyuan"]]
            remain = max(0, limit - len(gaiyuan))
            selected = gaiyuan + others[:remain]
            # 按原序重排
            sel_ids = {id(x) for x in selected}
            selected = [x for x in ordered if id(x) in sel_ids]

        lines = []
        dropped = max(0, len(ordered) - len(selected))
        for item in selected:
            text = item["event"]
            if item["count"] > 1 and not item["is_gaiyuan"]:
                text = f"{text.rstrip('。')}（凡 {item['count']} 见）。"
            prefix = item["time"] or ""
            lines.append(f"{prefix}：{text}" if prefix else text)

        if dropped > 0:
            lines.append(f"（其余同类事约 {dropped} 类从略，宜概括叙述。）")
        return lines

    def _events_for_emperor(self, emp):
        """按帝取编年：优先按事件记录的 emperor_id 匹配，旧档案退回尊号/姓名匹配。"""
        events = self.event_happened[1:] if len(self.event_happened) > 1 else []
        emp_id = emp.get("id")
        zunhao = (emp.get("zunhao") or "").strip()
        name = (emp.get("name") or "").strip()
        out = []
        for ev in events:
            text = ev.get("event") or ""
            if not text or text == "今年无事发生。":
                continue
            ev_emp_id = ev.get("emperor_id")
            if ev_emp_id is not None and emp_id is not None:
                if ev_emp_id == emp_id:
                    out.append(ev)
                continue
            label = (ev.get("emperor") or "").strip()
            if zunhao and label == zunhao:
                out.append(ev)
            elif not zunhao and name and label == name:
                out.append(ev)
        return out

    # —— 当今在位皇帝（局中导出时 listjson 尚无此帝）——

    def _has_reigning_emperor(self):
        """局中导出：王朝未亡且今上仍在位（未入 listjson）。"""
        return (
            not self.dynasty_die
            and bool(getattr(self, "ongame", False))
            and bool(self.emperor or self.current_emperor_pid)
        )

    def _current_emperor_as_emp(self):
        """把当今皇帝拼成与 listjson 条目同构的 dict，复用各格式化函数。"""
        return {
            "id": self.emperor_id,
            "pid": self.current_emperor_pid,
            "name": self.emperor,
            "zunhao": self.emperor_zunhao,
            "miaohao": "",
            "shihao": "",
        }

    def _current_reign_fortune_line(self):
        def _i(v):
            try:
                return int(round(float(v)))
            except (TypeError, ValueError):
                return None

        start = _i(getattr(self, "initial_dynasty_hp", None))
        now = _i(self.dynasty_hp)
        if start is None or now is None:
            return None
        peak = _i(getattr(self, "reign_peak_dynasty_hp", None))
        trough = _i(getattr(self, "reign_trough_dynasty_hp", None))
        peak = peak if peak is not None else max(start, now)
        trough = trough if trough is not None else min(start, now)
        return f"国运 {start}→峰{peak}/谷{trough}→今{now}"

    def _append_reigning_emperor_entry(self, lines):
        """帝系表末补「当今在位」一段。"""
        cur = self._current_emperor_as_emp()
        reign_years = self._reign_years()
        nianhao_summary = self.build_nianhao_summary(
            self.current_emperor_nianhao_history or []
        ) or (self.yearNumber or "（未知）")
        lines.append(f"当今在位　（尚未盖棺，无庙谥）　{self.emperor or '（未知）'}")
        prev_emp = self.listjson[-1] if self.listjson else None
        lines.append(f"　　与前代：{self._describe_emperor_kinship(prev_emp, cur)}")
        reign_desc = f"已在位约 {reign_years} 年" if reign_years >= 1 else "今岁甫即位"
        lines.append(
            f"　　年号：{nianhao_summary}　{reign_desc}　春秋 {self.emperor_age}　"
            f"材具：{self._ability_label(self.emperor_ab)}"
        )
        fortune = self._current_reign_fortune_line()
        if fortune:
            lines.append(f"　　{fortune}")
        lines.append(f"　　子嗣及封号：{self._format_emperor_children(cur)}")
        if self.emperor_zunhao:
            lines.append(f"　　（在位尊号：{self.emperor_zunhao}）")

    def _build_chronicle_section(self, lines):
        """编年要事：按 listjson 逐帝分段，压缩重复，并插入即位/驾崩/亡国；
        局中导出时末尾附当今皇帝已发生的纪事。"""
        lines.append("=" * 40)
        lines.append("【三、编年要事（已压缩，宜概括勿逐年照抄）】")

        emperors = list(self.listjson or [])
        n_emp = len(emperors)
        has_reigning = self._has_reigning_emperor()
        if not emperors and not has_reigning:
            lines.append("（本局尚无重大事件记录。）")
            return

        for gi, emp in enumerate(emperors):
            limit = self._PROMPT_EVENTS_PER_REIGN
            if n_emp > self._PROMPT_FULL_DETAIL_EMP_MAX:
                is_edge = gi < 2 or gi >= n_emp - 3
                if not is_edge:
                    limit = 3

            lines.append(f"—— {self._emp_display_name(emp)} ——")

            if gi == 0:
                lines.append("开国/即位：肇基立极，建元称制。")
            else:
                prev = emperors[gi - 1]
                kin = self._describe_emperor_kinship(prev, emp)
                lines.append(
                    f"即位：先帝崩，{emp.get('name', '')} 继统（{kin}）。"
                )

            reign_events = self._events_for_emperor(emp)
            compressed = self._compress_reign_events(reign_events, limit=limit)
            if compressed:
                for line in compressed:
                    lines.append(line)
            else:
                lines.append(
                    f"（在位约 {emp.get('jinian', 0)} 年，无重大随机纪事，宜据史评与国运虚写。）"
                )

            if gi == n_emp - 1 and self.dynasty_die:
                lines.append("亡国：国祚告终，帝运与俱尽。")
            elif gi < n_emp - 1 or has_reigning:
                lines.append(
                    f"崩：在位约 {emp.get('jinian', 0)} 年，"
                    f"庙号 {emp.get('miaohao') or '—'}，"
                    f"谥 {emp.get('shihao') or '—'}。"
                )

        if has_reigning:
            cur = self._current_emperor_as_emp()
            lines.append(f"—— 当今皇帝（{self.emperor or '（未知）'}）——")
            if emperors:
                kin = self._describe_emperor_kinship(emperors[-1], cur)
                lines.append(f"即位：先帝崩，{self.emperor or ''} 继统（{kin}）。")
            else:
                lines.append("开国/即位：肇基立极，建元称制。")
            reign_events = self._events_for_emperor(cur)
            compressed = self._compress_reign_events(reign_events)
            if compressed:
                for line in compressed:
                    lines.append(line)
            else:
                lines.append("（登基未久，尚无重大纪事。）")
            lines.append("（在位至今：此帝本纪写至当下即止，勿写其结局。）")

    def _build_fief_section(self, lines):
        """宗藩世家：王/郡王/国公级封国的承袭脉络，供「诸王世家」选用。"""
        collect = getattr(self, "collect_fiefs", None)
        if collect is None:
            return
        fiefs = [f for f in collect() if f.get("rank") in (1, 2)]
        if not fiefs:
            return

        lines.append("")
        lines.append("=" * 40)
        lines.append(
            "【四、宗藩世家（选用素材：可附「诸王世家」一节，亦可仅在各帝本纪中带出）】"
        )
        shown = fiefs[: self._PROMPT_FIEFS_MAX]
        for fief in shown:
            full_title = self.format_enfeoffed_title(fief["name"], fief["rank"])
            holders = fief.get("holders") or []
            labels = []
            for h in holders:
                label = h.name
                if h.shihao:
                    label += f"（谥 {h.shihao}）"
                labels.append(label)
            if len(labels) > self._PROMPT_FIEF_HOLDERS_MAX:
                head = labels[: self._PROMPT_FIEF_HOLDERS_MAX - 1]
                labels = head + ["……"] + [labels[-1]]
            chain = "、".join(labels) if labels else "（无考）"
            status = "已绝封" if fief.get("extinct") else "存续"
            lines.append(
                f"{full_title}（凡 {fief.get('total_count', len(holders))} 世，{status}）：{chain}"
            )
        if len(fiefs) > len(shown):
            lines.append(f"（其余 {len(fiefs) - len(shown)} 国从略。）")

    def _build_court_section(self, lines):
        """宰辅：历任首辅名录，供「宰辅列传」选用。"""
        history = getattr(self, "shoufu_history", None) or []
        if not history:
            return

        lines.append("")
        lines.append("=" * 40)
        lines.append(
            "【五、宰辅（选用素材：可附「宰辅列传」，亦可在各帝本纪中带出）】"
        )
        shown = list(history)
        if len(shown) > self._PROMPT_SHOUFU_MAX:
            head = shown[: self._PROMPT_SHOUFU_MAX - 3]
            dropped = len(shown) - self._PROMPT_SHOUFU_MAX
            shown = head + [None] + shown[-3:]
        else:
            dropped = 0
        for rec in shown:
            if rec is None:
                lines.append(f"（中间 {dropped} 任从略。）")
                continue
            if rec.get("end_year") is None:
                years = max(0, self.year - rec.get("start_year", self.year))
                if self.dynasty_die:
                    lines.append(
                        f"首辅{rec['name']}（材具：{self._ability_label(rec.get('ability'))}，"
                        f"在任 {years} 年，国亡时犹在任）"
                    )
                else:
                    lines.append(
                        f"当朝首辅{rec['name']}（材具：{self._ability_label(rec.get('ability'))}，"
                        f"在任 {years} 年——尚未盖棺，勿写其结局）"
                    )
            else:
                years = max(0, rec["end_year"] - rec.get("start_year", rec["end_year"]))
                exit_txt = rec.get("exit") or "去位"
                exit_txt = "卒于任" if exit_txt == "卒" else exit_txt
                lines.append(
                    f"首辅{rec['name']}（材具：{self._ability_label(rec.get('ability'))}，"
                    f"在任 {years} 年，{exit_txt}）"
                )

    def _phase_summary(self):
        """根据历代终局国运粗描全朝阶段。"""
        if not self.listjson:
            return ""
        ends = []
        for emp in self.listjson:
            try:
                ends.append(int(round(float(emp.get("dynasty_hp_end", 0)))))
            except (TypeError, ValueError):
                ends.append(0)
        if not ends:
            return ""
        parts = []
        if ends[0] >= 70:
            parts.append("开国强盛")
        elif ends[0] >= 40:
            parts.append("开国粗定")
        else:
            parts.append("开国艰难")
        mid = ends[len(ends) // 2] if len(ends) > 2 else ends[-1]
        if len(ends) > 2:
            peak = max(ends)
            if peak >= 80 and mid < peak - 20:
                parts.append("中叶转衰")
            elif peak >= 75:
                parts.append("中叶尚可")
            else:
                parts.append("中叶不振")
        if self.dynasty_die or ends[-1] <= 0:
            parts.append("末世倾覆")
        elif ends[-1] < 30:
            parts.append("末造危急")
        else:
            parts.append("国祚未绝")
        return " → ".join(parts)

    def _build_constraints(self, lines, n_emp, has_reigning):
        lines.append("【写作约束】")
        lines.append(
            "1. 硬事实不可改：帝系顺序、姓名、与前代关系、庙号谥号、年号、"
            "在位长短、享年、子嗣（含嗣位者）、终局存亡。"
        )
        lines.append(
            "2. 软演绎允许：性格、诏令细节、战场与宫廷情节——"
            "朝臣以【五、宰辅】所列首辅为准，可另虚构中下层官吏；"
            "须与各帝「史评」及国运盛衰方向一致。"
        )
        lines.append(
            "3. 编年已压缩：同类事勿逐年照抄，宜概括；改元、即位、崩殂、亡国须写清；"
            "改元事件所附缘由（灾异、祥瑞、武功等）须在正文中呼应。"
        )
        lines.append(
            "4. 称谓与文风：已故帝可用庙号（如「太宗」），叙其在位时事用姓名或「帝」；"
            "文言或浅近文言，庄重典雅。"
        )
        lines.append(
            "5. 语言与纪年：只用年号纪年，不得出现公元、世纪等现代纪年；"
            "正文不得出现「国运」「数据」「模拟」「史评」等系统词，"
            "亦不得夹杂现代口语或解释性括号。"
            "帝系表所附国运数字（满值100）仅供把握兴衰节奏，正文勿写任何数值。"
        )
        if n_emp <= 8:
            lines.append("6. 篇幅：可写完整本纪，每帝约四百至八百字。")
        elif n_emp <= 15:
            lines.append(
                "6. 篇幅：开国与末数帝从详，中间可略；全篇宜控制在可诵读长度。"
            )
        else:
            lines.append(
                "6. 篇幅：详开国、极盛/中兴与末三帝，中间诸帝「略曰」数语带过即可；"
                "若单次输出将尽，可在段落完结处以「（未完，俟续）」收束，待续写之令。"
            )
        if has_reigning:
            lines.append(
                "7. 当今皇帝尚未盖棺：其本纪写至当下即止，"
                "不得虚构其结局、庙号、谥号或身后事。"
            )

    def build_history_prompt(self):
        """将当前模拟状态整理成一段结构化的中文提示词。"""
        lines = []
        n_emp = len(self.listjson or [])
        has_reigning = self._has_reigning_emperor()

        lines.append("你是一位精通中国古代正史（如《二十四史》）笔法的史学家。")
        lines.append(
            "下面是一段【架空】王朝模拟数据。即使朝代名与真史重合，"
            "亦须严格按下列世系与结局书写，不得并入真实历史人物事迹。"
        )
        lines.append("")
        self._build_constraints(lines, n_emp, has_reigning)
        lines.append("")

        # —— 一、概况 ——
        lines.append("=" * 40)
        lines.append("【一、王朝概况】")
        lines.append(f"朝代：{self.dynasty or '（未命名）'}")
        lines.append(f"开国皇帝：{self._founder_name()}")
        lines.append(f"开国年号：{self._founder_nianhao()}")
        if self.zibei_poem:
            lines.append(
                f"字辈排行：{self.zibei_poem}"
                "（同辈宗室名讳共用其中一字，行文述及诸皇子时可据此体现辈分）"
            )
        else:
            lines.append("字辈排行：（无）")
        if has_reigning:
            lines.append(f"传世帝王：已盖棺 {n_emp} 位，另有当今皇帝在位")
        else:
            lines.append(f"传世帝王：{n_emp} 位")
        lines.append(f"国祚：约 {self.dynasty_age} 年")
        phase = self._phase_summary()
        if phase:
            lines.append(f"盛衰阶段：{phase}")
        if self.dynasty_die:
            lines.append(f"天下大势（终局）：{self.dynasty_st or '（未知）'}")
            lines.append("结局：王朝已亡，国祚终结。")
        else:
            lines.append(f"天下大势（当下）：{self.dynasty_st or '（未知）'}")
            lines.append("结局：王朝尚存，国史写至当下即可，勿写此后之事。")

        # —— 二、帝系本纪表（含国运）——
        lines.append("")
        lines.append("=" * 40)
        lines.append("【二、帝系本纪表】")
        if not self.listjson and not has_reigning:
            lines.append("（尚无已盖棺定论的帝王，请以开国皇帝的视角起笔。）")
        else:
            prev_emp = None
            for emp in self.listjson or []:
                miaohao = emp.get("miaohao") or "（无庙号）"
                shihao = emp.get("shihao") or "（无谥号）"
                nianhao = emp.get("nianhao") or "（无年号）"
                lines.append(
                    f"第 {emp.get('id')} 帝　{miaohao}　{shihao}　"
                    f"{emp.get('name', '')}"
                )
                lines.append(
                    f"　　与前代：{self._describe_emperor_kinship(prev_emp, emp)}"
                )
                lines.append(
                    f"　　年号：{nianhao}　在位约 {emp.get('jinian', 0)} 年　"
                    f"享年 {emp.get('age', 0)}　材具：{self._ability_label(emp.get('ab'))}"
                )
                fortune = self._reign_fortune_line(emp)
                if fortune:
                    lines.append(f"　　{fortune}")
                lines.append(f"　　子嗣及封号：{self._format_emperor_children(emp)}")
                verdict = emp.get("verdict")
                if verdict:
                    lines.append(f"　　史评：{verdict}")
                # 尊号降权：仅作附录，避免与谥号混淆
                zunhao = emp.get("zunhao")
                if zunhao:
                    lines.append(f"　　（在位尊号：{zunhao}）")
                prev_emp = emp
            if has_reigning:
                self._append_reigning_emperor_entry(lines)

        # —— 三、编年 ——
        lines.append("")
        self._build_chronicle_section(lines)

        # —— 四、宗藩（选用素材）——
        self._build_fief_section(lines)

        # —— 五、宰辅（选用素材）——
        self._build_court_section(lines)

        # —— 收束：输出要求 ——
        lines.append("")
        lines.append("=" * 40)
        lines.append("【输出要求】")
        lines.append(
            "请直接开始写作，勿复述本提示词、勿提问、勿加任何说明性开场白。全书结构："
        )
        lines.append("1. 自拟书名（如《周书》《大燕史略》），先作一段「序」，概述得国之由与一代兴亡大势；")
        lines.append("2. 依帝系表顺序，每帝一节「××本纪」，按编年要事叙述兴替；")
        if has_reigning:
            lines.append("3. 末节为当今皇帝，写至当下收笔，不作总评盖棺之论。")
        else:
            lines.append("3. 末附「史臣曰」，总评一代得失。")

        return "\n".join(lines)
