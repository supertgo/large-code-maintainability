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
        "--codeshovel-jar", required=True, help="Caminho do codeshovel.jar"
    )
    p_an.add_argument(
        "--workdir", default="./.lcm_work", help="Diretório de trabalho temporário"
    )
    p_an.add_argument(
        "--keep-clone", action="store_true", help="Não apagar clone temporário"
    )
    p_an.add_argument(
        "--incremental",
        action="store_true",
        help="Executa em modo incremental, salvando por método",
    )
    p_an.add_argument(
        "--results-dir",
        default="./fix_analysis_results",
        help="Pasta para salvar resultados incrementais",
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
        "--codeshovel-jar", required=True, help="Caminho do codeshovel.jar"
    )
    p_and.add_argument(
        "--incremental",
        action="store_true",
        help="Executa em modo incremental, salvando por método",
    )
    p_and.add_argument(
        "--results-dir",
        default="./fix_analysis_results",
        help="Pasta para salvar resultados incrementais",
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
        try:
            if is_git_url(args.repo):
                repo_path = clone_repo(args.repo, temp_root)
                clone_created = True
            else:
                repo_path = Path(args.repo).resolve()
                if not repo_path.exists() or not (repo_path / ".git").exists():
                    print(f"Caminho não é um repositório git válido: {repo_path}")
                    return 1

            if args.incremental:
                import os as _os

                results_dir = Path(args.results_dir).resolve()
                results_dir.mkdir(parents=True, exist_ok=True)

                # disponibiliza o caminho do JAR para o run_code_shovel
                _os.environ["CODESHOVEL_JAR"] = str(codeshovel_jar)

                # inicializa estrutura e executa pipeline incremental
                extract_single_repo(repo_path, results_dir)
                result_file = results_dir / f"{repo_path.name}_fix_analysis.json"
                extract_files_from_single_repo(repo_path, result_file)
                extract_methods_from_single_repo(repo_path, result_file)
                run_codeshovel(repo_path, result_file)

                # Gera gráficos e relatório usando o fix_analysis.py (incluindo HTML)
                analyzer = CodeShovelAnalyzer(str(codeshovel_jar), str(results_dir))
                analyzer.generate_from_saved_results()
                return 0
            else:
                code = analyze_single_repo(
                    repo_path, codeshovel_jar, keep_clone=args.keep_clone
                )
                return code
        finally:
            if clone_created and not args.keep_clone:
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

        if args.incremental:
            import os as _os

            results_dir = Path(args.results_dir).resolve()
            results_dir.mkdir(parents=True, exist_ok=True)

            _os.environ["CODESHOVEL_JAR"] = str(codeshovel_jar)

            repos = [
                d for d in repos_dir.iterdir() if d.is_dir() and (d / ".git").exists()
            ]
            repos.sort(key=lambda r: str(r).lower())

            for repo in repos:
                extract_single_repo(repo, results_dir)
                result_file = results_dir / f"{repo.name}_fix_analysis.json"
                extract_files_from_single_repo(repo, result_file)
                extract_methods_from_single_repo(repo, result_file)
                run_codeshovel(repo, result_file)

            # Gera gráficos e relatório agregado usando o fix_analysis.py (incluindo HTML)
            analyzer = CodeShovelAnalyzer(str(codeshovel_jar), str(results_dir))
            analyzer.generate_from_saved_results()
            return 0
        else:
            analyzer = CodeShovelAnalyzer(str(codeshovel_jar), str(repos_dir))
            analyses = analyzer.analyze_all_repositories()
            if analyses:
                analyzer.create_visualizations(analyses)
                analyzer.generate_report(analyses)
                analyzer.generate_html_report(analyses)
                return 0
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
