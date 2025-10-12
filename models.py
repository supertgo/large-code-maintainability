from dataclasses import dataclass
from typing import Dict, List, Optional

DEFAULT_RESULTS_DIR = "./fix_analysis_results_teste"
DEFAULT_REPOSITORIES_DIR = "./repos"

EXCLUDE_PATTERNS = [
    "test",
    "Test",
    "TEST",
    "target",
    "build",
    "out",
    ".git",
    "node_modules",
    "*.class",
    "*.jar",
    "*.war",
]


@dataclass
class CodeShovelMethodInfo:
    total_changes_count: int
    commit_count: int
    fix_commit_count: int
    fix_ratio: float


@dataclass
class MethodInfo:
    start_line: int
    end_line: int
    size_lines: int


@dataclass
class Method:
    name: str
    complete: bool
    method_info: MethodInfo
    codeshovel_analysis: Optional[CodeShovelMethodInfo] = None


@dataclass
class File:
    name: str
    path: str
    complete: bool
    methods: List[Method]


@dataclass
class Repository:
    name: str
    complete: bool
    files: List[File]
