#!/usr/bin/env python3
"""
LCM (Large Code Maintainability) - CLI

Uso rápido (um repositório):
  python large-code-maintainability/lcm_cli.py analyze --repo <path|git-url> \
         --codeshovel-jar <codeshovel.jar>

Exemplos:
  python large-code-maintainability/lcm_cli.py analyze \
    --repo https://github.com/spring-projects/spring-boot.git \
    --codeshovel-jar large-code-maintainability/codeshovel.jar

  python large-code-maintainability/lcm_cli.py analyze \
    --repo /path/para/repo/local \
    --codeshovel-jar large-code-maintainability/codeshovel.jar
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from fix_analysis import CodeShovelAnalyzer
from extract_repositories import extract_single_repo
from extract_files import extract_files_from_single_repo
from extract_methods import extract_methods_from_single_repo
from run_code_shovel import run_codeshovel


def is_git_url(repo: str) -> bool:
    return (
        repo.endswith(".git") or repo.startswith("git@") or repo.startswith("https://")
    )


def safe_rmdir(path: Path):
    if path.exists() and path.is_dir():
        shutil.rmtree(path)


def clone_repo(repo_url: str, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    clone_path = dest_dir / repo_name
    if clone_path.exists():
        return clone_path
    cmd = ["git", "clone", "--depth", "1", repo_url, str(clone_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Falha ao clonar {repo_url}: {result.stderr}")
    return clone_path


def analyze_single_repo(repo_path: Path, codeshovel_jar: Path, keep_clone: bool) -> int:
    repos_dir = repo_path.parent
    analyzer = CodeShovelAnalyzer(str(codeshovel_jar), str(repos_dir))
    analyses = analyzer.analyze_repository(repo_path.name)
    print(analyses[0].method_info.quality_metrics, "fjaklfjakflaj")
    if analyses:
        analyzer.save_results(repo_path.name, analyses)
        analyzer.create_visualizations(analyses)
        analyzer.generate_report(analyses)
        analyzer.generate_html_report(analyses)
        return 0
    return 2


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="lcm", description="Large Code Maintainability - CLI"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_an = sub.add_parser(
        "analyze", help="Analisa um único repositório (URL ou caminho)"
    )
    p_an.add_argument(
        "--repo", required=True, help="URL git ou caminho local do repositório"
    )
    p_an.add_argument(
        "--codeshovel-jar", 
        default="codeshovel.jar",
        help="Caminho do codeshovel.jar (padrão: codeshovel.jar)"
    )
    p_an.add_argument(
        "--workdir", default="./.lcm_work", help="Diretório de trabalho temporário"
    )
    p_an.add_argument(
        "--keep-clone", action="store_true", help="Não apagar clone temporário"
    )
    p_an.add_argument(
        "--results-dir",
        default=".",
        help="Pasta para salvar resultados incrementais (padrão: diretório atual)",
    )

    p_and = sub.add_parser(
        "analyze-dir", help="Analisa todos os repositórios dentro de uma pasta"
    )
    p_and.add_argument(
        "--repos-dir",
        required=True,
        help="Pasta contendo múltiplos repositórios git (subpastas com .git)",
    )
    p_and.add_argument(
        "--codeshovel-jar",
        default="codeshovel.jar",
        help="Caminho do codeshovel.jar (padrão: codeshovel.jar)"
    )
    p_and.add_argument(
        "--results-dir",
        default=".",
        help="Pasta para salvar resultados incrementais (padrão: diretório atual)",
    )

    args = parser.parse_args(argv)

    if args.command == "analyze":
        codeshovel_jar = Path(args.codeshovel_jar).resolve()
        if not codeshovel_jar.exists():
            print(f"codeshovel.jar não encontrado: {codeshovel_jar}")
            return 1

        temp_root = Path(args.workdir).resolve()
        temp_root.mkdir(parents=True, exist_ok=True)

        clone_created = False
        repo_path = None
        try:
            if is_git_url(args.repo):
                repo_path = clone_repo(args.repo, temp_root)
                clone_created = True
            else:
                repo_path = Path(args.repo).resolve()
                if not repo_path.exists() or not (repo_path / ".git").exists():
                    print(f"Caminho não é um repositório git válido: {repo_path}")
                    return 1

            import os as _os

            base_results_dir = Path(args.results_dir).resolve()
            base_results_dir.mkdir(parents=True, exist_ok=True)
            
            # Cria pasta específica para este repositório: <repo>_analysis
            repo_analysis_dir = base_results_dir / f"{repo_path.name}_analysis"
            repo_analysis_dir.mkdir(parents=True, exist_ok=True)

            # disponibiliza o caminho do JAR para o run_code_shovel
            _os.environ["CODESHOVEL_JAR"] = str(codeshovel_jar)

            result_file = repo_analysis_dir / f"{repo_path.name}_fix_analysis.json"
            
            # Check if file exists and has files (extraction already done)
            file_exists_with_files = False
            if result_file.exists():
                try:
                    with open(result_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict) and "files" in data and len(data["files"]) > 0:
                            file_exists_with_files = True
                except (json.JSONDecodeError, KeyError):
                    pass
            
            # Only run extraction if file doesn't exist or has no files
            if not file_exists_with_files:
                # inicializa estrutura e executa pipeline incremental
                extract_single_repo(repo_path, repo_analysis_dir)
                extract_files_from_single_repo(repo_path, result_file)
                extract_methods_from_single_repo(repo_path, result_file)
            
            # Run codeshovel
            try:
                run_codeshovel(repo_path, result_file)
            except KeyboardInterrupt:
                print("\n⚠️  Processo interrompido pelo usuário (Ctrl+C).")
                print(f"✅ Progresso salvo em {result_file.name}. Você pode continuar depois executando o mesmo comando.")
                return 130  # Standard exit code for SIGINT

            # Gera gráficos e relatório usando o fix_analysis.py (incluindo HTML)
            analyzer = CodeShovelAnalyzer(str(codeshovel_jar), str(repo_analysis_dir), str(repo_analysis_dir))
            analyzer.generate_from_saved_results()
            
            return 0
        finally:
            if clone_created and not args.keep_clone and repo_path is not None:
                # remove apenas o repositório clonado (não o workdir inteiro)
                safe_rmdir(repo_path)

    if args.command == "analyze-dir":
        codeshovel_jar = Path(args.codeshovel_jar).resolve()
        if not codeshovel_jar.exists():
            print(f"codeshovel.jar não encontrado: {codeshovel_jar}")
            return 1

        repos_dir = Path(args.repos_dir).resolve()
        if not repos_dir.exists() or not repos_dir.is_dir():
            print(f"Pasta inválida: {repos_dir}")
            return 1

        import os as _os

        base_results_dir = Path(args.results_dir).resolve()
        base_results_dir.mkdir(parents=True, exist_ok=True)

        _os.environ["CODESHOVEL_JAR"] = str(codeshovel_jar)

        repos = [
            d for d in repos_dir.iterdir() if d.is_dir() and (d / ".git").exists()
        ]
        repos.sort(key=lambda r: str(r).lower())

        for repo in repos:
            # Cria pasta específica para este repositório: <repo>_analysis
            repo_analysis_dir = base_results_dir / f"{repo.name}_analysis"
            repo_analysis_dir.mkdir(parents=True, exist_ok=True)
            
            result_file = repo_analysis_dir / f"{repo.name}_fix_analysis.json"
            
            # Check if file exists and has files (extraction already done)
            file_exists_with_files = False
            if result_file.exists():
                try:
                    with open(result_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict) and "files" in data and len(data["files"]) > 0:
                            file_exists_with_files = True
                except (json.JSONDecodeError, KeyError):
                    pass
            
            # Only run extraction if file doesn't exist or has no files
            if not file_exists_with_files:
                extract_single_repo(repo, repo_analysis_dir)
                extract_files_from_single_repo(repo, result_file)
                extract_methods_from_single_repo(repo, result_file)
            
            # Run codeshovel
            try:
                run_codeshovel(repo, result_file)
            except KeyboardInterrupt:
                print(f"\n⚠️  Processo interrompido pelo usuário (Ctrl+C) durante processamento de {repo.name}.")
                print(f"✅ Progresso salvo em {result_file.name}. Você pode continuar depois executando o mesmo comando.")
                return 130  # Standard exit code for SIGINT
            
            # Gera gráficos e relatório individual para este repositório
            analyzer = CodeShovelAnalyzer(str(codeshovel_jar), str(repo_analysis_dir), str(repo_analysis_dir))
            analyzer.generate_from_saved_results()

        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
