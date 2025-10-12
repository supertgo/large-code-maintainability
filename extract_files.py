from models import File, DEFAULT_REPOSITORIES_DIR, DEFAULT_RESULTS_DIR
from pathlib import Path
from dataclasses import asdict
import json

def extract_files_from_single_repo(repository: Path, result_path: Path):
    with open(result_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_paths = {file["path"] for file in data.get("files", [])}

    java_files = sorted(repository.rglob("*.java"), key=lambda f: str(f.name).lower())
    new_files = 0
    for java_file in java_files:
        if any(part in str(java_file) for part in ["test", "Test", "target", "build"]):
            continue

        rel_path = str(java_file.relative_to(repository))
        if rel_path in existing_paths:
            continue 

        file_json = File(
            name=java_file.name,
            path=str(java_file.relative_to(repository)),
            complete=False,
            methods=[]
        )
        data["files"].append(asdict(file_json))

        new_files += 1

    if new_files > 0:
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def extract_files_from_repos_dir(results_dir: Path, repositories_dir: Path):
    for repository in repositories_dir.iterdir():
        if repository.is_dir() and (repository / ".git").exists():
            result_path = results_dir / f"{repository.name}_fix_analysis.json"
            extract_files_from_single_repo(repository, result_path)

def main():
    extract_files_from_repos_dir(Path(DEFAULT_RESULTS_DIR), Path(DEFAULT_REPOSITORIES_DIR))

if __name__ == "__main__":
    main()
