from dataclasses import dataclass
from typing import Dict, List, Optional

DEFAULT_RESULTS_DIR = "./fix_analysis_results_teste"
DEFAULT_REPOSITORIES_DIR = "./repos"

@dataclass
class CodeShovelMethodInfo:
    commit_count: int
    fix_commit_count: int
    fix_ratio: float
    fix_commits: List[Dict]
    total_changes: List[Dict]

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
