#!/usr/bin/env python3
"""
CodeShovel Fix Analysis Tool

Este script analisa a relação entre o tamanho dos métodos e a frequência
de commits de "fix" usando o CodeShovel.

"""

import os
import json
import subprocess
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from collections import defaultdict
import argparse

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class MethodInfo:
    """Informações sobre um método"""

    name: str
    file_path: str
    start_line: int
    end_line: int
    size_lines: int
    repository: str
    commit_count: int
    fix_commit_count: int
    fix_ratio: float


@dataclass
class FixAnalysis:
    """Resultado da análise de fix"""

    method_info: MethodInfo
    fix_commits: List[Dict]
    total_changes: List[Dict]


class CodeShovelAnalyzer:
    """Analisador usando CodeShovel para métodos Java"""

    def __init__(self, codeshovel_jar_path: str, repositories_dir: str):
        """
        Inicializa o analisador

        Args:
            codeshovel_jar_path: Caminho para o JAR do CodeShovel
            repositories_dir: Diretório contendo os repositórios Java
        """
        self.codeshovel_jar_path = codeshovel_jar_path
        self.repositories_dir = Path(repositories_dir)
        self.results_dir = Path("fix_analysis_results_ed")
        self.results_dir.mkdir(exist_ok=True)

        if not os.path.exists(codeshovel_jar_path):
            raise FileNotFoundError(
                f"CodeShovel JAR não encontrado: {codeshovel_jar_path}"
            )

    def find_java_files(self, repo_path: Path) -> List[Path]:
        """Encontra todos os arquivos Java em um repositório"""
        java_files = []
        for java_file in repo_path.rglob("*.java"):
            if not any(
                part in str(java_file) for part in ["test", "Test", "target", "build"]
            ):
                java_files.append(java_file)
        return java_files

    def extract_methods_from_file(self, java_file: Path) -> List[Tuple[str, int, int]]:
        """
        Extrai informações básicas dos métodos de um arquivo Java
        Retorna: [(nome_metodo, linha_inicio, linha_fim)]
        """
        methods = []
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

                    method_name = re.search(r"(\w+) *\(", line_content).group(1)
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

        return methods

    def run_codeshovel(
        self, repo_path: str, file_path: str, method_name: str, start_line: int
    ) -> Optional[Dict]:
        """
        Executa o CodeShovel para um método específico

        Args:
            repo_path: Caminho para o repositório
            file_path: Caminho relativo do arquivo
            method_name: Nome do método
            start_line: Linha de início do método

        Returns:
            Dicionário com o resultado do CodeShovel ou None se falhar
        """
        try:
            cmd = [
                "java",
                "-jar",
                self.codeshovel_jar_path,
                "-repopath",
                repo_path,
                "-filepath",
                file_path,
                "-methodname",
                method_name,
                "-startline",
                str(start_line),
                "-outfile",
                f"temp_{method_name}_{start_line}.json",
            ]

            logger.info(f"Executando: {' '.join(cmd)}")

            # Executar comando
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                timeout=300,  # 5 minutos timeout
            )

            if result.returncode == 0:
                # Ler arquivo de saída
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
                logger.warning(f"CodeShovel falhou para {method_name}: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout ao executar CodeShovel para {method_name}")
        except Exception as e:
            logger.error(f"Erro ao executar CodeShovel: {e}")

        return None

    def analyze_fix_commits(self, codeshovel_data) -> Tuple[int, List[Dict]]:
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

    def analyze_repository(self, repo_name: str) -> List[FixAnalysis]:
        """
        Analisa um repositório completo

        Args:
            repo_name: Nome do repositório

        Returns:
            Lista de análises de fix para cada método
        """
        repo_path = self.repositories_dir / repo_name

        if not repo_path.exists():
            logger.warning(f"Repositório não encontrado: {repo_path}")
            return []

        logger.info(f"Analisando repositório: {repo_name}")

        java_files = self.find_java_files(repo_path)
        logger.info(f"Encontrados {len(java_files)} arquivos Java")

        analyses = []

        for java_file in java_files:
            try:
                methods = self.extract_methods_from_file(java_file)

                for method_name, start_line, end_line in methods:
                    size_lines = end_line - start_line + 1

                    relative_path = java_file.relative_to(repo_path)
                    codeshovel_data = self.run_codeshovel(
                        str(repo_path), str(relative_path), method_name, start_line
                    )

                    if codeshovel_data:
                        try:
                            total_commits, fix_commits = self.analyze_fix_commits(
                                codeshovel_data
                            )

                            if total_commits > 0:
                                method_info = MethodInfo(
                                    name=method_name,
                                    file_path=str(relative_path),
                                    start_line=start_line,
                                    end_line=end_line,
                                    size_lines=size_lines,
                                    repository=repo_name,
                                    commit_count=total_commits,
                                    fix_commit_count=len(fix_commits),
                                    fix_ratio=len(fix_commits) / total_commits,
                                )

                                all_changes = []
                                if (
                                    isinstance(codeshovel_data, dict)
                                    and "changeHistoryDetails" in codeshovel_data
                                ):
                                    all_changes = list(
                                        codeshovel_data["changeHistoryDetails"].values()
                                    )

                                analysis = FixAnalysis(
                                    method_info=method_info,
                                    fix_commits=fix_commits,
                                    total_changes=all_changes,
                                )

                                analyses.append(analysis)

                                logger.info(
                                    f"Método {method_name} ({size_lines} linhas): "
                                    f"{len(fix_commits)}/{total_commits} commits de fix"
                                )
                            else:
                                logger.info(
                                    f"Método {method_name} ({size_lines} linhas): sem commits de fix"
                                )
                        except Exception as e:
                            logger.error(
                                f"Erro ao processar dados do CodeShovel para {method_name}: {e}"
                            )
                            continue

            except Exception as e:
                logger.error(f"Erro ao analisar {java_file}: {e}")
                continue

        return analyses

    def analyze_all_repositories(self) -> List[FixAnalysis]:
        """Analisa todos os repositórios disponíveis"""
        all_analyses = []

        repos = [
            d
            for d in self.repositories_dir.iterdir()
            if d.is_dir() and (d / ".git").exists()
        ]

        logger.info(f"Encontrados {len(repos)} repositórios para análise")

        for repo in repos:
            try:
                file_path = Path(self.results_dir / f"{repo.name}_fix_analysis.json")

                if file_path.is_file():
                    with file_path.open("r", encoding="utf-8") as f:
                        data = json.load(f)
                        all_analyses.extend(data)
                    continue

                analyses = self.analyze_repository(repo.name)
                all_analyses.extend(analyses)

                self.save_results(repo.name, analyses)

            except Exception as e:
                logger.error(f"Erro ao analisar repositório {repo.name}: {e}")
                continue

        return all_analyses

    def save_results(self, repo_name: str, analyses: List[FixAnalysis]):
        """Salva resultados da análise"""
        results_file = self.results_dir / f"{repo_name}_fix_analysis.json"

        serializable_analyses = []
        for analysis in analyses:
            serializable_analysis = {
                "method_info": {
                    "name": analysis.method_info.name,
                    "file_path": analysis.method_info.file_path,
                    "start_line": analysis.method_info.start_line,
                    "end_line": analysis.method_info.end_line,
                    "size_lines": analysis.method_info.size_lines,
                    "repository": analysis.method_info.repository,
                    "commit_count": analysis.method_info.commit_count,
                    "fix_ratio": analysis.method_info.fix_ratio,
                },
                "fix_commit_count": len(analysis.fix_commits),
                "total_changes_count": len(analysis.total_changes),
            }
            serializable_analyses.append(serializable_analysis)

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(serializable_analyses, f, indent=2, ensure_ascii=False)

        logger.info(f"Resultados salvos em: {results_file}")

    def generate_statistics(self, analyses: List[FixAnalysis]) -> Dict:
        """Gera estatísticas gerais da análise"""
        if not analyses:
            return {}

        data = []
        for analysis in analyses:
            data.append(
                {
                    "method_name": analysis.method_info.name,
                    "repository": analysis.method_info.repository,
                    "size_lines": analysis.method_info.size_lines,
                    "commit_count": analysis.method_info.commit_count,
                    "fix_commit_count": analysis.method_info.fix_commit_count,
                    "fix_ratio": analysis.method_info.fix_ratio,
                }
            )

        df = pd.DataFrame(data)

        stats = {
            "total_methods": len(df),
            "total_repositories": df["repository"].nunique(),
            "avg_method_size": df["size_lines"].mean(),
            "median_method_size": df["size_lines"].median(),
            "avg_fix_ratio": df["fix_ratio"].mean(),
            "methods_with_fixes": len(df[df["fix_commit_count"] > 0]),
            "size_categories": {
                "small": len(df[df["size_lines"] <= 10]),
                "medium": len(df[(df["size_lines"] > 10) & (df["size_lines"] <= 50)]),
                "large": len(df[df["size_lines"] > 50]),
            },
        }

        # Análise por categoria de tamanho
        for category, mask in [
            ("small", df["size_lines"] <= 10),
            ("medium", (df["size_lines"] > 10) & (df["size_lines"] <= 50)),
            ("large", df["size_lines"] > 50),
        ]:
            if mask.sum() > 0:
                category_df = df[mask]
                stats[f"{category}_avg_fix_ratio"] = category_df["fix_ratio"].mean()
                stats[f"{category}_methods_count"] = len(category_df)

        return stats

    def create_visualizations(self, analyses: List[FixAnalysis]):
        """Cria visualizações dos resultados"""
        if not analyses:
            logger.warning("Nenhuma análise para visualizar")
            return

        # Converter para DataFrame
        data = []
        for analysis in analyses:
            data.append(
                {
                    "method_name": analysis.method_info.name,
                    "repository": analysis.method_info.repository,
                    "size_lines": analysis.method_info.size_lines,
                    "commit_count": analysis.method_info.commit_count,
                    "fix_commit_count": analysis.method_info.fix_commit_count,
                    "fix_ratio": analysis.method_info.fix_ratio,
                }
            )

        df = pd.DataFrame(data)

        # Configurar estilo
        plt.style.use("seaborn-v0_8")
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(
            "Análise de Relação entre Tamanho de Métodos e Commits de Fix", fontsize=16
        )

        axes[0, 0].scatter(df["size_lines"], df["fix_ratio"], alpha=0.6)
        axes[0, 0].set_xlabel("Tamanho do Método (linhas)")
        axes[0, 0].set_ylabel("Proporção de Commits de Fix")
        axes[0, 0].set_title("Tamanho vs Fix Ratio")
        axes[0, 0].grid(True, alpha=0.3)

        size_categories = pd.cut(
            df["size_lines"],
            bins=[0, 10, 50, float("inf")],
            labels=["Pequeno (≤10)", "Médio (11-50)", "Grande (>50)"],
        )
        df["size_category"] = size_categories

        df.boxplot(column="fix_ratio", by="size_category", ax=axes[0, 1])
        axes[0, 1].set_title("Fix Ratio por Categoria de Tamanho")
        axes[0, 1].set_xlabel("Categoria de Tamanho")
        axes[0, 1].set_ylabel("Fix Ratio")

        axes[1, 0].hist(df["size_lines"], bins=30, alpha=0.7, edgecolor="black")
        axes[1, 0].set_xlabel("Tamanho do Método (linhas)")
        axes[1, 0].set_ylabel("Frequência")
        axes[1, 0].set_title("Distribuição de Tamanhos de Métodos")
        axes[1, 0].grid(True, alpha=0.3)

        repo_stats = (
            df.groupby("repository")["fix_ratio"].mean().sort_values(ascending=False)
        )
        repo_stats.plot(kind="bar", ax=axes[1, 1])
        axes[1, 1].set_title("Fix Ratio Médio por Repositório")
        axes[1, 1].set_xlabel("Repositório")
        axes[1, 1].set_ylabel("Fix Ratio Médio")
        axes[1, 1].tick_params(axis="x", rotation=45)

        plt.tight_layout()

        output_file = self.results_dir / "fix_analysis_visualization.png"
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        logger.info(f"Visualização salva em: {output_file}")

        plt.show()

    def generate_report(self, analyses: List[FixAnalysis]):
        """Gera relatório completo da análise"""
        if not analyses:
            logger.warning("Nenhuma análise para relatório")
            return

        # Gerar estatísticas
        stats = self.generate_statistics(analyses)

        # Criar relatório
        report = f"""
        # Relatório de Análise de Fix vs Tamanho de Métodos

        ## Resumo Executivo
        - **Total de métodos analisados**: {stats.get("total_methods", 0)}
        - **Total de repositórios**: {stats.get("total_repositories", 0)}
        - **Métodos com commits de fix**: {stats.get("methods_with_fixes", 0)}
        - **Tamanho médio dos métodos**: {stats.get("avg_method_size", 0):.1f} linhas
        - **Proporção média de fix**: {stats.get("avg_fix_ratio", 0):.2%}

        ## Análise por Categoria de Tamanho

        ### Métodos Pequenos (≤10 linhas)
        - **Quantidade**: {stats.get("size_categories", {}).get("small", 0)}
        - **Fix ratio médio**: {stats.get("small_avg_fix_ratio", 0):.2%}

        ### Métodos Médios (11-50 linhas)
        - **Quantidade**: {stats.get("size_categories", {}).get("medium", 0)}
        - **Fix ratio médio**: {stats.get("medium_avg_fix_ratio", 0):.2%}

        ### Métodos Grandes (>50 linhas)
        - **Quantidade**: {stats.get("size_categories", {}).get("large", 0)}
        - **Fix ratio médio**: {stats.get("large_avg_fix_ratio", 0):.2%}

        ## Top 10 Métodos com Maior Fix Ratio
        """

        data = []
        for analysis in analyses:
            data.append(
                {
                    "method_name": analysis.method_info.name,
                    "repository": analysis.method_info.repository,
                    "size_lines": analysis.method_info.size_lines,
                    "fix_ratio": analysis.method_info.fix_ratio,
                    "fix_commit_count": analysis.method_info.fix_commit_count,
                }
            )

        df = pd.DataFrame(data)
        top_fix_methods = df.nlargest(10, "fix_ratio")

        for _, row in top_fix_methods.iterrows():
            report += f"- **{row['method_name']}** ({row['repository']}): {row['fix_ratio']:.2%} ({row['fix_commit_count']} fixes, {row['size_lines']} linhas)\n"

        report += f"""
        ## Conclusões
        Esta análise revela a relação entre o tamanho dos métodos e a frequência de commits de fix.
        Os resultados podem ajudar a entender se métodos maiores tendem a ter mais bugs ou se
        métodos menores são mais propensos a mudanças.

        ## Metodologia
        - Utilizou-se o CodeShovel para análise de histórico de métodos
        - Commits de fix foram identificados por palavras-chave: fix, bug, issue, problem, error
        - Métodos foram categorizados por tamanho: pequeno (≤10), médio (11-50), grande (>50)
        - Análise focou em repositórios Java de código aberto

        ---
        *Relatório gerado automaticamente pelo CodeShovel Fix Analysis Tool*
        """

        # Salvar relatório
        report_file = self.results_dir / "fix_analysis_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"Relatório salvo em: {report_file}")

        return report

    def create_visualizations_from_df(self, df: pd.DataFrame):
        """Cria visualizações dos resultados"""
        if df.empty:
            logger.warning("DataFrame vazio")
            return

        # Configurar estilo
        plt.style.use("seaborn-v0_8")
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(
            "Análise de Relação entre Tamanho de Métodos e Commits de Fix", fontsize=16
        )

        axes[0, 0].scatter(df["size_lines"], df["fix_ratio"], alpha=0.6)
        axes[0, 0].set_xlabel("Tamanho do Método (linhas)")
        axes[0, 0].set_ylabel("Proporção de Commits de Fix")
        axes[0, 0].set_title("Tamanho vs Fix Ratio")
        axes[0, 0].grid(True, alpha=0.3)

        size_categories = pd.cut(
            df["size_lines"],
            bins=[0, 10, 50, float("inf")],
            labels=["Pequeno (≤10)", "Médio (11-50)", "Grande (>50)"],
        )
        df["size_category"] = size_categories

        df.boxplot(column="fix_ratio", by="size_category", ax=axes[0, 1])
        axes[0, 1].set_title("Fix Ratio por Categoria de Tamanho")
        axes[0, 1].set_xlabel("Categoria de Tamanho")
        axes[0, 1].set_ylabel("Fix Ratio")

        axes[1, 0].hist(df["size_lines"], bins=30, alpha=0.7, edgecolor="black")
        axes[1, 0].set_xlabel("Tamanho do Método (linhas)")
        axes[1, 0].set_ylabel("Frequência")
        axes[1, 0].set_title("Distribuição de Tamanhos de Métodos")
        axes[1, 0].grid(True, alpha=0.3)

        repo_stats = (
            df.groupby("repository")["fix_ratio"].mean().sort_values(ascending=False)
        )
        repo_stats.plot(kind="bar", ax=axes[1, 1])
        axes[1, 1].set_title("Fix Ratio Médio por Repositório")
        axes[1, 1].set_xlabel("Repositório")
        axes[1, 1].set_ylabel("Fix Ratio Médio")
        axes[1, 1].tick_params(axis="x", rotation=45)

        plt.tight_layout()

        output_file = self.results_dir / "fix_analysis_visualization.png"
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        logger.info(f"Visualização salva em: {output_file}")

        plt.show()

    def generate_statistics_from_df(self, df: pd.DataFrame) -> Dict:
        """Gera estatísticas gerais da análise"""
        if df.empty:
            logger.warning("DataFrame vazio")
            return {}

        stats = {
            "total_methods": len(df),
            "total_repositories": df["repository"].nunique(),
            "avg_method_size": df["size_lines"].mean(),
            "median_method_size": df["size_lines"].median(),
            "avg_fix_ratio": df["fix_ratio"].mean(),
            "methods_with_fixes": len(df[df["fix_commit_count"] > 0]),
            "size_categories": {
                "small": len(df[df["size_lines"] <= 10]),
                "medium": len(df[(df["size_lines"] > 10) & (df["size_lines"] <= 50)]),
                "large": len(df[df["size_lines"] > 50]),
            },
        }

        # Análise por categoria de tamanho
        for category, mask in [
            ("small", df["size_lines"] <= 10),
            ("medium", (df["size_lines"] > 10) & (df["size_lines"] <= 50)),
            ("large", df["size_lines"] > 50),
        ]:
            if mask.sum() > 0:
                category_df = df[mask]
                stats[f"{category}_avg_fix_ratio"] = category_df["fix_ratio"].mean()
                stats[f"{category}_methods_count"] = len(category_df)

        return stats

    def generate_report_from_df(self, df: pd.DataFrame):
        """Gera relatório completo da análise"""
        if df.empty:
            logger.warning("DataFrame vazio")
            return

        # Gerar estatísticas
        stats = self.generate_statistics_from_df(df)

        # Criar relatório
        report = f"""
        # Relatório de Análise de Fix vs Tamanho de Métodos

        ## Resumo Executivo
        - **Total de métodos analisados**: {stats.get("total_methods", 0)}
        - **Total de repositórios**: {stats.get("total_repositories", 0)}
        - **Métodos com commits de fix**: {stats.get("methods_with_fixes", 0)}
        - **Tamanho médio dos métodos**: {stats.get("avg_method_size", 0):.1f} linhas
        - **Proporção média de fix**: {stats.get("avg_fix_ratio", 0):.2%}

        ## Análise por Categoria de Tamanho

        ### Métodos Pequenos (≤10 linhas)
        - **Quantidade**: {stats.get("size_categories", {}).get("small", 0)}
        - **Fix ratio médio**: {stats.get("small_avg_fix_ratio", 0):.2%}

        ### Métodos Médios (11-50 linhas)
        - **Quantidade**: {stats.get("size_categories", {}).get("medium", 0)}
        - **Fix ratio médio**: {stats.get("medium_avg_fix_ratio", 0):.2%}

        ### Métodos Grandes (>50 linhas)
        - **Quantidade**: {stats.get("size_categories", {}).get("large", 0)}
        - **Fix ratio médio**: {stats.get("large_avg_fix_ratio", 0):.2%}

        ## Top 10 Métodos com Maior Fix Ratio
        """

        top_fix_methods = df.nlargest(10, "fix_ratio")

        for _, row in top_fix_methods.iterrows():
            report += f"- **{row['method_name']}** ({row['repository']}): {row['fix_ratio']:.2%} ({row['fix_commit_count']} fixes, {row['size_lines']} linhas)\n"

        report += f"""
        ## Conclusões
        Esta análise revela a relação entre o tamanho dos métodos e a frequência de commits de fix.
        Os resultados podem ajudar a entender se métodos maiores tendem a ter mais bugs ou se
        métodos menores são mais propensos a mudanças.

        ## Metodologia
        - Utilizou-se o CodeShovel para análise de histórico de métodos
        - Commits de fix foram identificados por palavras-chave: fix, bug, issue, problem, error
        - Métodos foram categorizados por tamanho: pequeno (≤10), médio (11-50), grande (>50)
        - Análise focou em repositórios Java de código aberto

        ---
        *Relatório gerado automaticamente pelo CodeShovel Fix Analysis Tool*
        """

        # Salvar relatório
        report_file = self.results_dir / "fix_analysis_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"Relatório salvo em: {report_file}")

        return report

    def load_results(self) -> List[Dict]:
        all_results = []
        for file in self.results_dir.glob("*_fix_analysis.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    all_results.extend(data)
                logger.info(f"Carregado: {file}")
            except Exception as e:
                logger.warning(f"Erro ao carregar {file}: {e}")
        return all_results

    def generate_from_saved_results(self):
        analyses = self.load_results()

        if not analyses:
            logger.warning("Nenhum resultado encontrado na pasta")
            return

        df = pd.DataFrame([
            {
                "method_name": item["method_info"]["name"],
                "repository": item["method_info"]["repository"],
                "size_lines": item["method_info"]["size_lines"],
                "commit_count": item["method_info"]["commit_count"],
                "fix_commit_count": item["fix_commit_count"],
                "fix_ratio": item["method_info"]["fix_ratio"],
            }
            for item in analyses
        ])

        self.create_visualizations_from_df(df)
        self.generate_report_from_df(df)
        stats = self.generate_statistics_from_df(df)
        logger.info(f"Estatísticas: {stats}")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="CodeShovel Fix Analysis Tool")
    parser.add_argument(
        "--codeshovel-jar", required=True, help="Caminho para o JAR do CodeShovel"
    )
    parser.add_argument(
        "--repositories-dir",
        required=True,
        help="Diretório contendo os repositórios Java",
    )
    parser.add_argument(
        "--repo-limit",
        type=int,
        default=5,
        help="Limite de repositórios para analisar (padrão: 5)",
    )
    parser.add_argument(
        "--method-limit",
        type=int,
        default=50,
        help="Limite de métodos por repositório (padrão: 50)",
    )

    args = parser.parse_args()

    try:
        analyzer = CodeShovelAnalyzer(args.codeshovel_jar, args.repositories_dir)

        logger.info("Iniciando análise de repositórios...")

        analyses = analyzer.analyze_all_repositories()

        if analyses:
            logger.info(f"Análise concluída! {len(analyses)} métodos analisados.")

            stats = analyzer.generate_statistics(analyses)
            logger.info(f"Estatísticas: {stats}")

            analyzer.create_visualizations(analyses)

            analyzer.generate_report(analyses)

            logger.info(
                "Análise completa! Verifique os arquivos na pasta 'fix_analysis_results'"
            )
        else:
            logger.warning(
                "Nenhuma análise foi gerada. Verifique os parâmetros e repositórios."
            )

    except Exception as e:
        logger.error(f"Erro durante a execução: {e}")
        raise


if __name__ == "__main__":
    main()
