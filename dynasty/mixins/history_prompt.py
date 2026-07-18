# -*- coding: utf-8 -*-
"""根据整局模拟结果，一键生成「让 AI 撰写完整国史」的提示词。"""


class HistoryPromptMixin:
    """汇总本局朝代、历代帝王、纪事与国运轨迹，拼装成可复制的国史写作提示词。"""

    def _describe_emperor_kinship(self, prev_emp, cur_emp):
        """描述当代皇帝与上一代皇帝的父系亲属关系，供国史行文交代世系承继。"""
        if prev_emp is None:
            return "开国之君，肇基立业"
        prev_p = self.get_person_by_id(prev_emp.get("pid")) if prev_emp.get("pid") else None
        cur_p = self.get_person_by_id(cur_emp.get("pid")) if cur_emp.get("pid") else None
        if prev_p is None or cur_p is None:
            return "承继前代（世系不详）"
        relation = self.describe_kinship(cur_p, prev_p)
        return f"为前代（{prev_emp.get('name', '')}）之{relation}"

    def build_history_prompt(self):
        """将当前模拟状态整理成一段结构化的中文提示词。"""
        lines = []

        lines.append("你是一位精通中国古代正史（如《二十四史》）笔法的史学家。")
        lines.append(
            "下面是一段架空王朝模拟的完整数据，请据此撰写一部体例完整、"
            "文风典雅的编年体 / 纪传体国史。"
        )
        lines.append("")
        lines.append("写作要求：")
        lines.append("1. 仿正史笔法，文言与浅近文言为主，庄重典雅；")
        lines.append("2. 结构包含：开国本纪、历代帝王本纪、重大事件纪事、以及末尾的「史臣曰」总评；")
        lines.append("3. 依据下列数据合理演绎史实细节、人物性格与因果，但不得改变既定的帝王世系、年号与结局；")
        lines.append("4. 国运数值仅供你把握王朝盛衰节奏，不必在正文中直接出现数字。")
        lines.append("")
        lines.append("=" * 40)
        lines.append("【一、王朝概况】")
        lines.append(f"朝代：{self.dynasty or '（未命名）'}")
        lines.append(f"开国皇帝（起名）：{self.emperor or '（未知）'}")
        lines.append(f"开国年号：{self.yearNumber or '（未知）'}")
        lines.append(f"字辈排行：{self.zibei_poem or '（无）'}")
        lines.append(f"传世帝王：{len(self.listjson)} 位")
        lines.append(f"国祚：约 {self.dynasty_age} 年")
        lines.append(f"天下大势（终局）：{self.dynasty_st or '（未知）'}")
        if self.dynasty_die:
            lines.append("结局：王朝已亡，国祚终结。")
        else:
            lines.append("结局：王朝尚存（模拟进行中）。")

        lines.append("")
        lines.append("=" * 40)
        lines.append("【二、历代帝王】")
        if not self.listjson:
            lines.append("（尚无已盖棺定论的帝王，请以开国皇帝的视角起笔。）")
        else:
            prev_emp = None
            for emp in self.listjson:
                miaohao = emp.get("miaohao") or "（无庙号）"
                shihao = emp.get("shihao") or "（无谥号）"
                nianhao = emp.get("nianhao") or "（无年号）"
                zunhao = emp.get("zunhao") or "（无尊号）"
                seg = (
                    f"第 {emp.get('id')} 帝　庙号：{miaohao}　谥号：{shihao}　"
                    f"姓名：{emp.get('name', '')}"
                )
                lines.append(seg)
                lines.append(f"　　尊号：{zunhao}")
                lines.append(f"　　与前代关系：{self._describe_emperor_kinship(prev_emp, emp)}")
                lines.append(
                    f"　　年号：{nianhao}　在位约 {emp.get('jinian', 0)} 年　"
                    f"享年 {emp.get('age', 0)}　治国手腕：{emp.get('ab', 0)}/9"
                )
                verdict = emp.get("verdict")
                if verdict:
                    lines.append(f"　　史评：{verdict}")
                prev_emp = emp

        lines.append("")
        lines.append("=" * 40)
        lines.append("【三、王朝纪事（编年）】")
        events = self.event_happened[1:] if len(self.event_happened) > 1 else []
        # 过滤「今年无事发生」等空白事件，只保留有信息量的纪事
        meaningful = [
            ev for ev in events
            if ev.get("event") and ev.get("event") != "今年无事发生。"
        ]
        if not meaningful:
            lines.append("（本局尚无重大事件记录。）")
        else:
            for ev in meaningful:
                time_str = ev.get("time", "")
                emp_str = ev.get("emperor", "")
                event_str = ev.get("event", "")
                prefix = f"{time_str}"
                if emp_str:
                    prefix += f"（{emp_str}）"
                lines.append(f"{prefix}：{event_str}")

        lines.append("")
        lines.append("=" * 40)
        lines.append("【四、国运盛衰轨迹】")
        history = getattr(self, "dynasty_hp_history", None) or []
        if not history:
            lines.append("（无国运数据。）")
        else:
            # 数据可能逐年很多，按皇帝分段给出起止国运，避免提示词过长
            segments = []
            cur = None
            for rec in history:
                eid = rec.get("emperor_id")
                if cur is None or cur["emperor_id"] != eid:
                    if cur is not None:
                        segments.append(cur)
                    cur = {
                        "emperor_id": eid,
                        "emperor": rec.get("emperor", ""),
                        "start_hp": rec.get("hp", 0),
                        "end_hp": rec.get("hp", 0),
                        "peak": rec.get("hp", 0),
                        "trough": rec.get("hp", 0),
                    }
                else:
                    hp = rec.get("hp", 0)
                    cur["end_hp"] = hp
                    cur["peak"] = max(cur["peak"], hp)
                    cur["trough"] = min(cur["trough"], hp)
            if cur is not None:
                segments.append(cur)
            for seg in segments:
                lines.append(
                    f"{seg['emperor']} 一朝：国运自 {seg['start_hp']} 起，"
                    f"最盛 {seg['peak']}，最衰 {seg['trough']}，终于 {seg['end_hp']}"
                    "（满值 100）"
                )

        lines.append("")
        lines.append("=" * 40)
        lines.append(
            "请综合以上数据，写出这部王朝的完整国史。开篇简述开国之由，"
            "中叙历代兴替与重大事件，末以「史臣曰」评断一代之得失。"
        )

        return "\n".join(lines)
