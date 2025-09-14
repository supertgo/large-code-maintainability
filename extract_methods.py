from dataclasses import asdict
from models import CodeShovelMethodInfo, Method, MethodInfo, DEFAULT_REPOSITORIES_DIR, DEFAULT_RESULTS_DIR
from pathlib import Path
import json
import re
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def extract_methods_from_file(file_path: str, repo_name: str, repositories_dir: Path):
    methods = []
    java_file = repositories_dir / repo_name / file_path
    try:
        with open(java_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        in_method = False
        method_start = 0
        method_name = ""
        brace_count = 0

        for i, line in enumerate(lines, 1):
            line_content = line.strip()

            # Detectar início de método (padrão simplificado)
            if re.match(
                r"^\s*(public|private|protected|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *\{?",
                line_content,
            ):
                if in_method:
                    methods.append((method_name, method_start, i - 1))

                match = re.search(r"(\w+) *\(", line_content)
                if match:
                    method_name = match.group(1)
                else:
                    method_name = f"unknown_method_at_line_{i}"
                method_start = i
                in_method = True
                brace_count = 1 if line_content.endswith("{") else 0

            elif in_method:
                if line_content.endswith("{"):
                    brace_count += 1
                elif line_content.endswith("}"):
                    brace_count -= 1
                    if brace_count == 0:
                        methods.append((method_name, method_start, i))
                        in_method = False

        if in_method:
            methods.append((method_name, method_start, len(lines)))

    except Exception as e:
        logger.warning(f"Erro ao processar {java_file}: {e}")

    methods = sorted(methods, key=lambda x: (x[0], x[1]))
    return methods

def extract_methods(repositories_dir: Path, results_dir: Path):
    for result in results_dir.iterdir():
        with open(result, "r", encoding="utf-8") as f:
            data = json.load(f)

        for file in data["files"]:
            methods = extract_methods_from_file(file["path"], data["name"], Path(DEFAULT_REPOSITORIES_DIR))
            for method_name, start_line, end_line in methods:
                method_info_json = MethodInfo(
                    start_line=start_line,
                    end_line=end_line,
                    size_lines=end_line - start_line + 1
                )

                method_json = Method(
                    name=method_name,
                    complete=False,
                    method_info=method_info_json,
                    codeshovel_analysis=None
                )

                file["methods"].append(asdict(method_json))

        with open(result, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    extract_methods(Path(DEFAULT_REPOSITORIES_DIR), Path(DEFAULT_RESULTS_DIR))

if __name__ == "__main__":
    main()
