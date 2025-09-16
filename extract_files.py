from models import File, DEFAULT_REPOSITORIES_DIR, DEFAULT_RESULTS_DIR
from pathlib import Path
from dataclasses import asdict
import json

def extract_files(results_dir: Path, repositories_dir: Path):
    java_files = []

    for result in results_dir.iterdir():
        with open(result, "r", encoding="utf-8") as f:
            data = json.load(f)
            repo_path = repositories_dir / data["name"]

        java_files = sorted(repo_path.rglob("*.java"), key=lambda f: str(f.name).lower())
        for java_file in java_files:
            if not any(
                part in str(java_file) for part in ["test", "Test", "target", "build"]
            ):
                file_json = File(
                    name=java_file.name,
                    path=str(java_file.relative_to(repo_path)),
                    complete=False,
                    methods=[]
                )

                data["files"].append(asdict(file_json))

        with open(result, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    extract_files(Path(DEFAULT_RESULTS_DIR), Path(DEFAULT_REPOSITORIES_DIR))

if __name__ == "__main__":
    main()
