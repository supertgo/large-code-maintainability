from dataclasses import asdict
from models import DEFAULT_REPOSITORIES_DIR, DEFAULT_RESULTS_DIR, CodeShovelMethodInfo
from pathlib import Path
from typing import Dict, List, Tuple
import json
import logging
import subprocess
import os
import argparse
import sys
import signal
from extract_repositories import extract_single_repo
from extract_files import extract_files_from_single_repo
from extract_methods import extract_methods_from_single_repo

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_requested = False

def signal_handler(signum, frame):
    """Handle interrupt signals gracefully"""
    global shutdown_requested
    logger.info("\nInterrupt received. Finishing current method and saving progress...")
    shutdown_requested = True

def save_data_atomically(data: dict, file_path: Path):
    """
    Save JSON data atomically to avoid corruption on interruption.
    Writes to a temporary file first, then renames it.
    """
    try:
        # Create temporary file in the same directory
        temp_file = file_path.with_suffix(file_path.suffix + '.tmp')
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # Atomic rename (works on Unix and Windows)
        temp_file.replace(file_path)
    except Exception as e:
        logger.error(f"Error saving data atomically: {e}")
        # Fallback to direct write if atomic write fails
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def analyze_fix_commits(codeshovel_data) -> Tuple[int, List[Dict]]:
    """
    Analisa commits de fix nos dados do CodeShovel

    Args:
        codeshovel_data: Dados retornados pelo CodeShovel

    Returns:
        (total_commits, fix_commits)
    """
    fix_commits = []
    total_commits = 0

    if not isinstance(codeshovel_data, dict):
        logger.warning(
            f"Dados do CodeShovel não são um dicionário válido: {type(codeshovel_data)}"
        )
        return 0, []

    if "changeHistoryDetails" not in codeshovel_data:
        logger.warning(
            "Campo 'changeHistoryDetails' não encontrado nos dados do CodeShovel"
        )
        return 0, []

    change_details = codeshovel_data["changeHistoryDetails"]

    if not isinstance(change_details, dict):
        logger.warning(
            f"changeHistoryDetails não é um dicionário: {type(change_details)}"
        )
        return 0, []

    for commit_sha, commit_data in change_details.items():
        if not isinstance(commit_data, dict):
            logger.warning(
                f"Detalhes do commit {commit_sha} não são um dicionário: {type(commit_data)}"
            )
            continue

        total_commits += 1

        commit_message = commit_data.get("commitMessage", "").lower()
        if any(
            keyword in commit_message
            for keyword in ["fix", "bug", "issue", "problem", "error"]
        ):
            fix_commits.append(commit_data)

    return total_commits, fix_commits

def get_code_shovel_data(repository: Path, file_path: str, method_name: str, start_line: int):
    try:
        cmd = [
            "java",
            "-jar",
            "codeshovel.jar",
            "-repopath",
            str(repository),
            "-filepath",
            str(file_path),
            "-methodname",
            method_name,
            "-startline",
            str(start_line),
            "-outfile",
            f"temp_{method_name}_{start_line}.json",
        ]

        logger.info(f"Executando: {' '.join(cmd)}")

        # Executar comando
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=300,  # 5 minutos timeout
        )

        if process.returncode == 0:
            output_file = f"temp_{method_name}_{start_line}.json"
            if os.path.exists(output_file):
                try:
                    with open(output_file, "r", encoding="utf-8") as f:
                        content = f.read().strip()

                        if not content:
                            logger.warning(f"Arquivo de saída vazio: {output_file}")
                            os.remove(output_file)
                            return None

                        try:
                            data = json.loads(content)
                            logger.debug(
                                f"CodeShovel retornou dados válidos para {method_name}"
                            )
                        except json.JSONDecodeError as e:
                            logger.warning(
                                f"Erro ao fazer parse do JSON para {method_name}: {e}"
                            )
                            logger.debug(f"Conteúdo do arquivo: {content[:200]}...")
                            os.remove(output_file)
                            return None

                        os.remove(output_file)
                        return data
                except Exception as e:
                    logger.error(f"Erro ao ler arquivo de saída {output_file}: {e}")
                    if os.path.exists(output_file):
                        os.remove(output_file)
                    return None
            else:
                logger.warning(f"Arquivo de saída não encontrado: {output_file}")
        else:
            logger.warning(f"CodeShovel falhou para {method_name}: {process.stderr}")

    except subprocess.TimeoutExpired:
        logger.warning(f"Timeout ao executar CodeShovel para {method_name}")
    except Exception as e:
        logger.error(f"Erro ao executar CodeShovel: {e}")

    return None

def run_codeshovel(repository: Path, result_path: Path):
    """
    Runs codeshovel on all methods in the repository.
    If the result file doesn't exist, creates it first using extract_repositories, extract_files, and extract_methods.
    After all methods are processed, deletes the result file.
    Handles interruptions gracefully, saving progress before exiting.
    """
    global shutdown_requested
    shutdown_requested = False  # Reset flag for this repository
    
    # Check if result file exists
    if not result_path.exists():
        logger.info(f"Result file does not exist for {repository.name}. Creating it...")
        # Create the repository structure
        extract_single_repo(repository, result_path.parent)
        # Extract files
        extract_files_from_single_repo(repository, result_path)
        # Extract methods
        extract_methods_from_single_repo(repository, result_path)
        logger.info(f"Result file created for {repository.name}")
    
    # Read the data
    try:
        with open(result_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error reading result file (may be corrupted): {e}")
        logger.info("Attempting to recover by recreating the file...")
        # Recreate the file
        extract_single_repo(repository, result_path.parent)
        extract_files_from_single_repo(repository, result_path)
        extract_methods_from_single_repo(repository, result_path)
        with open(result_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    # Process all files and methods
    for file in data["files"]:
        if shutdown_requested:
            logger.info("Shutdown requested. Saving progress and exiting...")
            save_data_atomically(data, result_path)
            logger.info(f"Progress saved. You can resume by running the same command again.")
            return
        
        methods_completed = 0
        if file["complete"]:
            methods_completed = len(file["methods"])
        else:
            for method in file["methods"]:
                if shutdown_requested:
                    logger.info("Shutdown requested. Saving progress and exiting...")
                    save_data_atomically(data, result_path)
                    logger.info(f"Progress saved. You can resume by running the same command again.")
                    return
                
                if method["complete"]:
                    methods_completed += 1
                    continue

                codeshovel_data = get_code_shovel_data(repository, file["path"], method["name"], method["method_info"]["start_line"])
                if codeshovel_data is not None:
                    method["complete"] = True
                    methods_completed += 1

                    total_commits, fix_commits = analyze_fix_commits(codeshovel_data)

                    all_changes = []
                    if (isinstance(codeshovel_data, dict) and "changeHistoryDetails" in codeshovel_data):
                        all_changes = list(
                            codeshovel_data["changeHistoryDetails"].values()
                        )

                    codeshovel_info = CodeShovelMethodInfo(
                        commit_count = total_commits,
                        fix_commit_count = len(fix_commits),
                        fix_ratio = len(fix_commits) / total_commits if total_commits > 0 else 0,
                        total_changes_count = len(all_changes)
                    )

                    method["codeshovel_analysis"] = asdict(codeshovel_info)

                    # Save progress after each method (atomically)
                    save_data_atomically(data, result_path)

            file["complete"] = (methods_completed == len(file["methods"]))
            # Save file completion state
            save_data_atomically(data, result_path)

    # Check if all files and methods are complete
    all_complete = True
    if not data.get("files"):
        all_complete = False
    else:
        for file in data["files"]:
            if not file.get("complete", False):
                all_complete = False
                break
            # Check all methods in the file are complete
            for method in file.get("methods", []):
                if not method.get("complete", False):
                    all_complete = False
                    break
            if not all_complete:
                break

    # If all methods are processed, delete the result file
    if all_complete:
        logger.info(f"All methods processed for {repository.name}. Deleting result file...")
        result_path.unlink()
        logger.info(f"Result file deleted for {repository.name}")

def main():
    """
    Main function that processes repositories based on CLI arguments.
    For each repository:
    - If result file exists, only runs codeshovel
    - If result file doesn't exist, creates it first (extract_repositories, extract_files, extract_methods), then runs codeshovel
    - After all methods are processed, deletes the result file
    Handles interruptions gracefully, saving progress before exiting.
    """
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    parser = argparse.ArgumentParser(
        description="Run CodeShovel analysis on Java repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a specific repository
  python run_code_shovel.py --repo ./repos/spring-boot

  # Analyze a repository with custom results directory
  python run_code_shovel.py --repo ./repos/spring-boot --results-dir ./my_results

  # Analyze all repositories in a directory
  python run_code_shovel.py --repos-dir ./repos
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--repo",
        type=str,
        help="Path to a specific repository to analyze"
    )
    group.add_argument(
        "--repos-dir",
        type=str,
        help="Path to directory containing multiple repositories to analyze"
    )
    
    parser.add_argument(
        "--results-dir",
        type=str,
        default=DEFAULT_RESULTS_DIR,
        help=f"Directory to store temporary results (default: {DEFAULT_RESULTS_DIR})"
    )
    
    args = parser.parse_args()
    
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    
    repositories_to_process = []
    
    if args.repo:
        # Single repository specified
        repo_path = Path(args.repo)
        if not repo_path.exists():
            logger.error(f"Repository path does not exist: {repo_path}")
            sys.exit(1)
        if not repo_path.is_dir():
            logger.error(f"Repository path is not a directory: {repo_path}")
            sys.exit(1)
        if not (repo_path / ".git").exists():
            logger.error(f"Repository path is not a Git repository: {repo_path}")
            sys.exit(1)
        repositories_to_process.append(repo_path)
    elif args.repos_dir:
        # Directory of repositories specified
        repos_dir = Path(args.repos_dir)
        if not repos_dir.exists():
            logger.error(f"Repositories directory does not exist: {repos_dir}")
            sys.exit(1)
        if not repos_dir.is_dir():
            logger.error(f"Repositories path is not a directory: {repos_dir}")
            sys.exit(1)
        
        for repository in repos_dir.iterdir():
            if repository.is_dir() and (repository / ".git").exists():
                repositories_to_process.append(repository)
        
        if not repositories_to_process:
            logger.warning(f"No Git repositories found in: {repos_dir}")
            sys.exit(1)
    
    # Process all repositories
    for repository in repositories_to_process:
        result_path = results_dir / f"{repository.name}_fix_analysis.json"
        logger.info(f"Processing repository: {repository.name} ({repository})")
        run_codeshovel(repository, result_path)

if __name__ == "__main__":
    main()
