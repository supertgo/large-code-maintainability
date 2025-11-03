from dataclasses import asdict
from models import DEFAULT_REPOSITORIES_DIR, DEFAULT_RESULTS_DIR, CodeShovelMethodInfo
from pathlib import Path
from typing import Dict, List, Tuple
import json
import logging
import subprocess
import os

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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

def get_code_shovel_data(repository: Path, file_path: Path, method_name: str, start_line: int):
    try:
        jar_path = os.environ.get("CODESHOVEL_JAR", "codeshovel.jar")
        cmd = [
            "java",
            "-jar",
            jar_path,
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
                        return data;
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
    with open(result_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for file in data["files"]:
        methods_completed = 0
        if file["complete"]:
            continue

        for method in file["methods"]:
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

                with open(result_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

        file["complete"] = (methods_completed == len(file["methods"]))

def main():
    # for repository in Path(DEFAULT_REPOSITORIES_DIR).iterdir():
    #     if repository.is_dir() and (repository / ".git").exists():
    #         result_path = Path(DEFAULT_RESULTS_DIR) / f"{repository.name}_fix_analysis.json"
    #         run_codeshovel(repository, result_path)
    run_codeshovel((Path(DEFAULT_REPOSITORIES_DIR) / "elasticsearch"), Path(DEFAULT_RESULTS_DIR) / "elasticsearch_fix_analysis.json")

if __name__ == "__main__":
    main()
