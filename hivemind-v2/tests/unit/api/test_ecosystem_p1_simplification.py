"""Tests for v1.6.0 P1 simplification: lower popularity_floor defaults."""

from __future__ import annotations

from aiteam.api.routes.ecosystem import _DEFAULT_SCAN_PROFILE


class TestDefaultScanProfileThresholds:
    def test_github_floor_is_1000(self):
        """GitHub popularity_floor defaults to 1000 (down from 5000)."""
        assert _DEFAULT_SCAN_PROFILE["popularity_floor"]["github"] == 1000

    def test_huggingface_floor_is_200(self):
        """HuggingFace popularity_floor defaults to 200 monthly downloads."""
        assert _DEFAULT_SCAN_PROFILE["popularity_floor"]["huggingface"] == 200

    def test_npm_floor_is_1000(self):
        """npm popularity_floor defaults to 1000 weekly downloads (down from 5000)."""
        assert _DEFAULT_SCAN_PROFILE["popularity_floor"]["npm"] == 1000

    def test_pypi_floor_is_1000(self):
        """PyPI popularity_floor defaults to 1000 (down from 5000)."""
        assert _DEFAULT_SCAN_PROFILE["popularity_floor"]["pypi"] == 1000

    def test_alert_thresholds_unchanged(self):
        """max_new_per_scan alert threshold is unchanged at 50."""
        assert _DEFAULT_SCAN_PROFILE["alert_thresholds"]["max_new_per_scan"] == 50

    def test_all_four_sources_present(self):
        """All four data source keys are present in popularity_floor."""
        keys = set(_DEFAULT_SCAN_PROFILE["popularity_floor"].keys())
        assert keys >= {"github", "huggingface", "npm", "pypi"}
