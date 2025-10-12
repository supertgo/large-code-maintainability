from dataclasses import asdict
from models import Method, MethodInfo, DEFAULT_REPOSITORIES_DIR, DEFAULT_RESULTS_DIR
from pathlib import Path
import json
import re
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def extract_methods_from_file(file_path: str, repo_name: str, repository: Path):
    methods = []
    java_file = repository / file_path
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

def extract_methods_from_single_repo(repository: Path, result_path: Path):
    with open(result_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    new_methods_total = 0        

    for file in data["files"]:
        methods = extract_methods_from_file(file["path"], data["name"], repository)

        existing_methods = {m["name"] for m in file.get("methods", [])}
        new_methods = 0

        for method_name, start_line, end_line in methods:
            if method_name in existing_methods:
                continue 

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
            new_methods += 1

        new_methods_total += new_methods

    if new_methods_total > 0:
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def extract_methods(repositories_dir: Path, results_dir: Path):
    for repository in repositories_dir.iterdir():
        if repository.is_dir() and (repository / ".git").exists():
            result_path = results_dir / f"{repository.name}_fix_analysis.json"
            extract_methods_from_single_repo(repository, result_path)

def main():
    extract_methods(Path(DEFAULT_REPOSITORIES_DIR), Path(DEFAULT_RESULTS_DIR))

if __name__ == "__main__":
    main()
