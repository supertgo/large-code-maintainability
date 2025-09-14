from models import Repository, DEFAULT_REPOSITORIES_DIR, DEFAULT_RESULTS_DIR
from pathlib import Path
from dataclasses import asdict
import json

def extract_repos(repositories_dir: Path, results_dir: Path):
    results_dir.mkdir(parents=True, exist_ok=True)

    repositories = [
        d
        for d in repositories_dir.iterdir()
        if d.is_dir() and (d / ".git").exists()
    ]

    repositories.sort(key=lambda r: str(r).lower())

    for repository in repositories:
        results_file = results_dir / f"{repository.name}_fix_analysis.json"
        repo_json = Repository(
            name=repository.name,
            complete=False,
            files = []
        )

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(asdict(repo_json), f, indent=2, ensure_ascii=False)

def main():
    extract_repos(Path(DEFAULT_REPOSITORIES_DIR), Path(DEFAULT_RESULTS_DIR))

if __name__ == "__main__":
    main()
