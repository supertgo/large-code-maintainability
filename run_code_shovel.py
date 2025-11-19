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

        # Tentar diferentes campos possíveis para a mensagem do commit
        commit_message = (
            commit_data.get("commitMessage", "") or 
            commit_data.get("message", "") or 
            commit_data.get("msg", "") or
            str(commit_data.get("commit", {}).get("message", "")) if isinstance(commit_data.get("commit"), dict) else ""
        )
        
        # Log apenas para o primeiro commit para debug
        if total_commits == 1:
            logger.debug(f"Estrutura do commit - campos: {list(commit_data.keys())}")
            logger.debug(f"Mensagem do commit (primeiros 200 chars): '{commit_message[:200]}'")
        
        commit_message_lower = commit_message.lower()
        
        # Palavras-chave expandidas para detectar commits de fix
        fix_keywords = [
            "fix", "bug", "issue", "problem", "error", "bugfix", 
            "hotfix", "patch", "resolve", "correct", "repair", "debug",
            "fixed", "fixes", "fixing", "resolved", "resolves", "resolving",
            "correction", "corrections", "bug fix", "fix bug"
        ]
        
        if commit_message_lower and any(keyword in commit_message_lower for keyword in fix_keywords):
            fix_commits.append(commit_data)

    return total_commits, fix_commits

def get_code_shovel_data(repository: Path, file_path, method_name: str, start_line: int):
    try:
        # Converter file_path para Path se for string
        if isinstance(file_path, str):
            file_path_obj = Path(file_path)
        else:
            file_path_obj = file_path
        
        # Verificar se o arquivo existe no repositório
        full_file_path = repository / file_path_obj
        if not full_file_path.exists():
            logger.warning(f"Arquivo Java não encontrado no repositório: {full_file_path}")
            return None
        
        jar_path = os.environ.get("CODESHOVEL_JAR", "codeshovel.jar")
        cmd = [
            "java",
            "-jar",
            jar_path,
            "-repopath",
            str(repository),
            "-filepath",
            str(file_path_obj),  # Usar caminho relativo ao repositório
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

        output_file = f"temp_{method_name}_{start_line}.json"
        
        if process.returncode == 0:
            if os.path.exists(output_file):
                try:
                    with open(output_file, "r", encoding="utf-8") as f:
                        content = f.read().strip()

                        if not content:
                            logger.warning(f"Arquivo de saída vazio: {output_file}")
                            if process.stderr:
                                logger.debug(f"Stderr do CodeShovel: {process.stderr}")
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
                # Arquivo não encontrado mesmo com returncode 0
                logger.warning(f"Arquivo de saída não encontrado: {output_file}")
                logger.warning(f"Método: {method_name}, Arquivo: {file_path}, Linha: {start_line}")
                if process.stdout:
                    logger.info(f"Stdout do CodeShovel: {process.stdout[:500]}")
                if process.stderr:
                    logger.info(f"Stderr do CodeShovel: {process.stderr[:500]}")
                # Verificar se o arquivo foi criado em outro lugar
                current_dir = os.getcwd()
                logger.debug(f"Procurando arquivo no diretório atual: {current_dir}")
        else:
            logger.warning(f"CodeShovel falhou para {method_name} (código {process.returncode})")
            if process.stderr:
                logger.warning(f"Erro do CodeShovel: {process.stderr[:500]}")
            if process.stdout:
                logger.debug(f"Stdout do CodeShovel: {process.stdout[:500]}")

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
            # Se o arquivo já está completo, conta todos os métodos como completos
            methods_completed = len(file.get("methods", []))
            continue

        for method in file["methods"]:
            if method["complete"]:
                methods_completed += 1
                continue

            codeshovel_data = get_code_shovel_data(repository, file["path"], method["name"], method["method_info"]["start_line"])
            
            # Marca como completo mesmo se não retornou dados (para evitar tentativas infinitas)
            method["complete"] = True
            methods_completed += 1
            
            if codeshovel_data is not None:
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
            else:
                # Se não retornou dados, marca com valores zero
                codeshovel_info = CodeShovelMethodInfo(
                    commit_count = 0,
                    fix_commit_count = 0,
                    fix_ratio = 0.0,
                    total_changes_count = 0
                )
                method["codeshovel_analysis"] = asdict(codeshovel_info)

            # Salva o progresso após processar cada método
            with open(result_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        was_complete = file.get("complete", False)
        file["complete"] = (methods_completed == len(file["methods"]))
        # Save file state if completion status changed
        if not was_complete and file["complete"]:
            with open(result_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Salva o estado final após processar todos os arquivos
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    # for repository in Path(DEFAULT_REPOSITORIES_DIR).iterdir():
    #     if repository.is_dir() and (repository / ".git").exists():
    #         result_path = Path(DEFAULT_RESULTS_DIR) / f"{repository.name}_fix_analysis.json"
    #         run_codeshovel(repository, result_path)
    run_codeshovel((Path(DEFAULT_REPOSITORIES_DIR) / "elasticsearch"), Path(DEFAULT_RESULTS_DIR) / "elasticsearch_fix_analysis.json")

if __name__ == "__main__":
    main()
