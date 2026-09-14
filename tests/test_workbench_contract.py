"""GNN 组员工作台的信息架构契约。

这些测试只检查入口文案和生成结果的结构，不把历史数字当作科研结论，
也不需要 RDKit/Streamlit/浏览器。
"""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEMBERS = ("王启龙", "宁显泷", "衣思淼", "代维斯丹", "王散曼")


def test_member_markdown_has_current_task_before_history():
    for name in MEMBERS:
        text = (ROOT / name / "工作台.md").read_text(encoding="utf-8")
        current = text.index("## 当前任务（本周先做）")
        history = text.index("## 历史复核任务（保留，不代表当前科研结论")
        assert current < history, name
        assert "AIDD 主库" in text[current:history]
        assert any(token in text[current:history] for token in ("不产出新排名", "不打新候选榜", "不产生候选榜", "不把旧 Top-10"))


def test_member_html_keeps_functional_tabs_and_layers():
    required_tabs = (
        "🧭 我的工作台", "🔬 全线流程", "📍 本周看板", "🗓 学期总览",
        "📋 周卡片·打卡", "📚 学习资源", "✅ 打卡台账", "💾 数据管理",
    )
    for name in MEMBERS:
        text = (ROOT / name / f"打卡_{name}.html").read_text(encoding="utf-8")
        assert "现在先做什么" in text, name
        assert "当前正式研究链" in text, name
        assert "历史复核任务与技术参数" in text, name
        assert "current-review-banner" in text, name
        assert "candidate_release=false" in text, name
        assert "github.com/wang13236614835-cmyk/aidd" in text, name
        for tab in required_tabs:
            assert tab in text, f"{name}: {tab}"


def test_generator_is_source_of_member_pages():
    generator = (ROOT / "tools" / "gen_member_pages.py").read_text(encoding="utf-8")
    assert "CURRENT_CONTEXT" in generator
    assert "历史复核任务与当前任务分层" in generator
    assert "AIDD_STATE" in generator
    assert "MEMBERS_WITH_LEADER" not in generator


def test_current_state_does_not_claim_candidate_release():
    state = (ROOT / "STATUS.json").read_text(encoding="utf-8")
    assert '"candidate_release": false' in state
    assert '"gnn_enable_gate": "closed"' in state
