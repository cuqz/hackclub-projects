"""Stage 类别映射测试。"""
import pytest

from aiteam.pipeline.class_map import STAGE_CLASS_MAP, get_stage_class


class TestStageClassMap:
    def test_all_plan_stages(self):
        plan_stages = ["research", "meeting", "decompose", "review", "diagnose", "report", "decision"]
        for stage in plan_stages:
            assert STAGE_CLASS_MAP[stage] == "Plan", f"{stage} should be Plan"

    def test_all_execute_stages(self):
        for stage in ["implement", "fix"]:
            assert STAGE_CLASS_MAP[stage] == "Execute", f"{stage} should be Execute"

    def test_all_verify_stages(self):
        for stage in ["test", "retest"]:
            assert STAGE_CLASS_MAP[stage] == "Verify", f"{stage} should be Verify"

    def test_all_template_stages_covered(self):
        # All stages from the 7 templates in docs/pipeline-redesign.md
        template_stages = {
            "research", "meeting", "decompose", "implement", "test", "review",
            "retest", "diagnose", "fix", "report", "decision",
        }
        for stage in template_stages:
            assert stage in STAGE_CLASS_MAP, f"{stage} missing from STAGE_CLASS_MAP"


class TestGetStageClass:
    def test_research_returns_plan(self):
        assert get_stage_class("research") == "Plan"

    def test_implement_returns_execute(self):
        assert get_stage_class("implement") == "Execute"

    def test_test_returns_verify(self):
        assert get_stage_class("test") == "Verify"

    def test_unknown_stage_raises_value_error(self):
        with pytest.raises(ValueError, match="unknown stage"):
            get_stage_class("nonexistent_stage")

    def test_template_override_takes_precedence(self):
        overrides = {"research": "Execute"}
        assert get_stage_class("research", template_overrides=overrides) == "Execute"

    def test_template_override_does_not_affect_other_stages(self):
        overrides = {"research": "Execute"}
        assert get_stage_class("implement", template_overrides=overrides) == "Execute"

    def test_none_overrides_falls_back_to_default(self):
        assert get_stage_class("review", template_overrides=None) == "Plan"

    def test_empty_overrides_falls_back_to_default(self):
        assert get_stage_class("fix", template_overrides={}) == "Execute"

    def test_unknown_stage_with_override_match(self):
        overrides = {"custom_stage": "Plan"}
        assert get_stage_class("custom_stage", template_overrides=overrides) == "Plan"

    def test_unknown_stage_without_override_raises(self):
        with pytest.raises(ValueError):
            get_stage_class("custom_stage")
