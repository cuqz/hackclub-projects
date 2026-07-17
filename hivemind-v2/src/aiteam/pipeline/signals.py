"""Pass/Fail 信号识别 — 基于正则白名单判断测试/构建工具的输出语义。"""
import re

# Pass 信号正则白名单（qa-eng R1 决议）
PASS_PATTERNS: list[re.Pattern] = [
    re.compile(r'\b\d+ passed\b', re.IGNORECASE),           # pytest: "5 passed"
    re.compile(r'\ball tests passed\b', re.IGNORECASE),      # 通用
    re.compile(r'\bOK\s*\(\d+ tests\)', re.IGNORECASE),      # unittest: "OK (5 tests)"
    re.compile(r'✓'),                                         # 单元符号（mocha/jest 等）
    re.compile(r'\bPASS\b'),                                  # 大写 PASS
    re.compile(r'\b100%\s+passed\b', re.IGNORECASE),         # "100% passed"
    re.compile(r'\bbuild\s+success(?:ful)?\b', re.IGNORECASE),  # "build successful"
    re.compile(r'\bAll \d+ tests? (?:pass|pass(?:ed)?)\b', re.IGNORECASE),  # "All 3 tests pass"
    re.compile(r'\bTests run: \d+.*Failures: 0.*Errors: 0\b', re.IGNORECASE),  # Maven
    re.compile(r'\bno failures\b', re.IGNORECASE),
]

# Fail 关键字列表（exit_code 非零即 fail，stdout 含以下任一也判 fail）
_FAIL_KEYWORDS: list[re.Pattern] = [
    re.compile(r'\bfailed\b', re.IGNORECASE),
    re.compile(r'\bfailure\b', re.IGNORECASE),
    re.compile(r'[Ee]rror\b'),              # "error", "Error", "SyntaxError:", "IOError"
    re.compile(r'\bTraceback\b'),
    re.compile(r'\bException\b'),
    re.compile(r'\bFAIL\b'),
    re.compile(r'\bERROR\b'),
    re.compile(r'\bAborted\b', re.IGNORECASE),
]


def is_pass_signal(stdout: str, exit_code: int) -> bool:
    """同时要求 exit_code == 0 且 stdout 含至少一个 PASS 模式。"""
    if exit_code != 0:
        return False
    return any(p.search(stdout) for p in PASS_PATTERNS)


def is_fail_signal(stdout: str, exit_code: int) -> bool:
    """exit_code != 0 或 stdout 含 fail/error/traceback 关键字时返回 True。"""
    if exit_code != 0:
        return True
    return any(p.search(stdout) for p in _FAIL_KEYWORDS)
