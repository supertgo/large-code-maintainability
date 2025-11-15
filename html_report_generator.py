#!/usr/bin/env python3
"""
Módulo para geração de relatórios HTML com gráficos e análises

Este módulo contém toda a lógica necessária para gerar relatórios HTML
a partir de dados de análise de métodos.
"""

import base64
import logging
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd

logger = logging.getLogger(__name__)


class HTMLReportGenerator:
    """Gerador de relatórios HTML com gráficos e análises"""

    def __init__(self, output_dir: Path = Path("fix_analysis_results")):
        """
        Inicializa o gerador de relatórios HTML

        Args:
            output_dir: Diretório onde o HTML será salvo
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def create_charts(self, df: pd.DataFrame) -> List[str]:
        """
        Cria gráficos e retorna como strings base64

        Args:
            df: DataFrame com os dados da análise

        Returns:
            Lista de strings base64 representando os gráficos
        """
        charts = []

        # Configurar estilo
        plt.style.use("seaborn-v0_8")

        # Gráfico 1: Scatter plot - Tamanho vs Fix Ratio
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(df["size_lines"], df["fix_ratio"], alpha=0.6, c="#2E86AB", s=50)
        ax.set_xlabel("Tamanho do Método (linhas)", fontsize=12)
        ax.set_ylabel("Proporção de Commits de Fix", fontsize=12)
        ax.set_title("Tamanho vs Fix Ratio", fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3)

        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        buf.seek(0)
        charts.append(base64.b64encode(buf.read()).decode("utf-8"))
        plt.close()

        # Gráfico 2: Boxplot - Fix Ratio por Categoria
        fig, ax = plt.subplots(figsize=(10, 6))
        size_categories = pd.cut(
            df["size_lines"],
            bins=[0, 10, 50, float("inf")],
            labels=["Pequeno (≤10)", "Médio (11-50)", "Grande (>50)"],
        )
        df_temp = df.copy()
        df_temp["size_category"] = size_categories
        df_temp.boxplot(column="fix_ratio", by="size_category", ax=ax)
        ax.set_title(
            "Fix Ratio por Categoria de Tamanho", fontsize=14, fontweight="bold"
        )
        ax.set_xlabel("Categoria de Tamanho", fontsize=12)
        ax.set_ylabel("Fix Ratio", fontsize=12)
        plt.suptitle("")

        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        buf.seek(0)
        charts.append(base64.b64encode(buf.read()).decode("utf-8"))
        plt.close()

        # Gráfico 3: Histograma - Distribuição de Tamanhos
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(
            df["size_lines"], bins=30, alpha=0.7, color="#A23B72", edgecolor="black"
        )
        ax.set_xlabel("Tamanho do Método (linhas)", fontsize=12)
        ax.set_ylabel("Frequência", fontsize=12)
        ax.set_title(
            "Distribuição de Tamanhos de Métodos", fontsize=14, fontweight="bold"
        )
        ax.grid(True, alpha=0.3)

        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        buf.seek(0)
        charts.append(base64.b64encode(buf.read()).decode("utf-8"))
        plt.close()

        # Gráfico 4: Barras - Fix Ratio Médio por Repositório
        fig, ax = plt.subplots(figsize=(10, 6))
        repo_stats = (
            df.groupby("repository")["fix_ratio"].mean().sort_values(ascending=False)
        )
        repo_stats.plot(kind="bar", ax=ax, color="#F18F01")
        ax.set_title(
            "Fix Ratio Médio por Repositório", fontsize=14, fontweight="bold"
        )
        ax.set_xlabel("Repositório", fontsize=12)
        ax.set_ylabel("Fix Ratio Médio", fontsize=12)
        ax.tick_params(axis="x", rotation=45)

        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        buf.seek(0)
        charts.append(base64.b64encode(buf.read()).decode("utf-8"))
        plt.close()

        # Gráfico 5: Scatter plot - Complexidade Ciclomática vs Fix Ratio
        if "cyclomatic_complexity" in df.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            scatter = ax.scatter(
                df["cyclomatic_complexity"],
                df["fix_ratio"],
                alpha=0.6,
                c=df["size_lines"],
                cmap="viridis",
                s=50,
            )
            ax.set_xlabel("Complexidade Ciclomática", fontsize=12)
            ax.set_ylabel("Proporção de Commits de Fix", fontsize=12)
            ax.set_title(
                "Complexidade Ciclomática vs Fix Ratio", fontsize=14, fontweight="bold"
            )
            ax.grid(True, alpha=0.3)
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label("Tamanho (linhas)", fontsize=10)

            buf = BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            buf.seek(0)
            charts.append(base64.b64encode(buf.read()).decode("utf-8"))
            plt.close()

            # Gráfico 6: Boxplot - Fix Ratio por Categoria de Complexidade
            fig, ax = plt.subplots(figsize=(10, 6))
            complexity_categories = pd.cut(
                df["cyclomatic_complexity"],
                bins=[0, 5, 10, float("inf")],
                labels=["Baixa (≤5)", "Média (6-10)", "Alta (>10)"],
            )
            df_temp = df.copy()
            df_temp["complexity_category"] = complexity_categories
            df_temp.boxplot(column="fix_ratio", by="complexity_category", ax=ax)
            ax.set_title(
                "Fix Ratio por Categoria de Complexidade",
                fontsize=14,
                fontweight="bold",
            )
            ax.set_xlabel("Categoria de Complexidade", fontsize=12)
            ax.set_ylabel("Fix Ratio", fontsize=12)
            plt.suptitle("")

            buf = BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            buf.seek(0)
            charts.append(base64.b64encode(buf.read()).decode("utf-8"))
            plt.close()

            # Gráfico 7: Histograma - Distribuição de Complexidade Ciclomática
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(
                df["cyclomatic_complexity"],
                bins=30,
                alpha=0.7,
                color="#6A4C93",
                edgecolor="black",
            )
            ax.set_xlabel("Complexidade Ciclomática", fontsize=12)
            ax.set_ylabel("Frequência", fontsize=12)
            ax.set_title(
                "Distribuição de Complexidade Ciclomática",
                fontsize=14,
                fontweight="bold",
            )
            ax.grid(True, alpha=0.3)

            buf = BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            buf.seek(0)
            charts.append(base64.b64encode(buf.read()).decode("utf-8"))
            plt.close()

            # Gráfico 8: Scatter 3D simulado - Tamanho vs Complexidade (colorido por Fix Ratio)
            fig, ax = plt.subplots(figsize=(10, 6))
            scatter = ax.scatter(
                df["size_lines"],
                df["cyclomatic_complexity"],
                c=df["fix_ratio"],
                cmap="RdYlGn_r",
                s=100,
                alpha=0.6,
                edgecolors="black",
                linewidth=0.5,
            )
            ax.set_xlabel("Tamanho do Método (linhas)", fontsize=12)
            ax.set_ylabel("Complexidade Ciclomática", fontsize=12)
            ax.set_title(
                "Tamanho vs Complexidade (colorido por Fix Ratio)",
                fontsize=14,
                fontweight="bold",
            )
            ax.grid(True, alpha=0.3)
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label("Fix Ratio", fontsize=10)

            buf = BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            buf.seek(0)
            charts.append(base64.b64encode(buf.read()).decode("utf-8"))
            plt.close()

        return charts

    def generate_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Gera estatísticas a partir do DataFrame

        Args:
            df: DataFrame com os dados da análise

        Returns:
            Dicionário com estatísticas
        """
        if df.empty:
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

        # Análise por complexidade ciclomática (se disponível)
        if "cyclomatic_complexity" in df.columns:
            stats["avg_complexity"] = df["cyclomatic_complexity"].mean()
            stats["median_complexity"] = df["cyclomatic_complexity"].median()
            stats["max_complexity"] = df["cyclomatic_complexity"].max()
            
            stats["complexity_categories"] = {
                "low": len(df[df["cyclomatic_complexity"] <= 5]),
                "medium": len(
                    (df["cyclomatic_complexity"] > 5)
                    & (df["cyclomatic_complexity"] <= 10)
                ),
                "high": len(df[df["cyclomatic_complexity"] > 10]),
            }

            # Análise por categoria de complexidade
            for category, mask in [
                ("low", df["cyclomatic_complexity"] <= 5),
                ("medium", (df["cyclomatic_complexity"] > 5) & (df["cyclomatic_complexity"] <= 10)),
                ("high", df["cyclomatic_complexity"] > 10),
            ]:
                if mask.sum() > 0:
                    category_df = df[mask]
                    stats[f"complexity_{category}_avg_fix_ratio"] = category_df["fix_ratio"].mean()
                    stats[f"complexity_{category}_methods_count"] = len(category_df)

        return stats

    def generate_html(
        self, df: pd.DataFrame, output_filename: str = "fix_analysis_report.html"
    ) -> Optional[Path]:
        """
        Gera o relatório HTML completo

        Args:
            df: DataFrame com os dados da análise
            output_filename: Nome do arquivo HTML de saída

        Returns:
            Path do arquivo HTML gerado ou None em caso de erro
        """
        if df.empty:
            logger.warning("DataFrame vazio, não é possível gerar HTML")
            return None

        # Gerar estatísticas
        stats = self.generate_statistics(df)

        # Criar gráficos
        logger.info("Gerando gráficos...")
        charts = self.create_charts(df)

        # Top 10 métodos com maior fix ratio
        top_fix_methods = df.nlargest(10, "fix_ratio")

        # Gerar HTML
        logger.info("Criando HTML...")
        html_content = self._build_html_template(stats, charts, top_fix_methods)

        # Salvar HTML
        html_file = self.output_dir / output_filename
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Relatório HTML salvo em: {html_file}")
        return html_file

    def _build_html_template(
        self, stats: Dict, charts: List[str], top_fix_methods: pd.DataFrame
    ) -> str:
        """
        Constrói o template HTML

        Args:
            stats: Dicionário com estatísticas
            charts: Lista de gráficos em base64
            top_fix_methods: DataFrame com top 10 métodos

        Returns:
            String contendo o HTML completo
        """
        # Gerar lista de top métodos
        top_methods_html = ""
        for idx, (_, row) in enumerate(top_fix_methods.iterrows(), 1):
            top_methods_html += f"""
                    <div class="method-item">
                        <strong>{idx}. {row['method_name']}</strong>
                        <br>
                        <span>Repositório: {row['repository']} | Fix Ratio: {row['fix_ratio']:.2%} | Fixes: {row['fix_commit_count']} | Tamanho: {row['size_lines']} linhas</span>
                    </div>
"""

        html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Análise de Fix vs Tamanho de Métodos</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .stat-card h3 {{
            color: #667eea;
            font-size: 1em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section h2 {{
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .section h3 {{
            color: #764ba2;
            font-size: 1.3em;
            margin-top: 25px;
            margin-bottom: 15px;
        }}
        
        .chart {{
            margin: 30px 0;
            text-align: center;
        }}
        
        .chart img {{
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .category-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .category-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .category-card h4 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .category-card p {{
            margin: 5px 0;
            color: #555;
        }}
        
        .method-list {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        
        .method-item {{
            padding: 15px;
            margin: 10px 0;
            background: white;
            border-radius: 6px;
            border-left: 4px solid #764ba2;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        
        .method-item strong {{
            color: #667eea;
            font-size: 1.1em;
        }}
        
        .method-item span {{
            color: #777;
            font-size: 0.9em;
        }}
        
        .methodology {{
            background: #fff3cd;
            padding: 25px;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
            margin: 30px 0;
        }}
        
        .methodology h3 {{
            color: #856404;
            margin-bottom: 15px;
        }}
        
        .methodology ul {{
            margin-left: 20px;
            color: #856404;
        }}
        
        .methodology li {{
            margin: 8px 0;
        }}
        
        footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #777;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .content {{
                padding: 20px;
            }}
            
            header h1 {{
                font-size: 1.8em;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Relatório de Análise de Fix vs Tamanho de Métodos</h1>
            <p>Análise de Manutenibilidade de Código com CodeShovel</p>
        </header>
        
        <div class="content">
            <div class="section">
                <h2>Resumo Executivo</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Métodos Analisados</h3>
                        <div class="value">{stats.get("total_methods", 0)}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Repositórios</h3>
                        <div class="value">{stats.get("total_repositories", 0)}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Métodos com Fixes</h3>
                        <div class="value">{stats.get("methods_with_fixes", 0)}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Tamanho Médio</h3>
                        <div class="value">{stats.get("avg_method_size", 0):.1f}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Fix Ratio Médio</h3>
                        <div class="value">{stats.get("avg_fix_ratio", 0):.1%}</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Visualizações</h2>
                
                <div class="chart">
                    <h3>Tamanho vs Fix Ratio</h3>
                    <img src="data:image/png;base64,{charts[0]}" alt="Tamanho vs Fix Ratio">
                </div>
                
                <div class="chart">
                    <h3>Fix Ratio por Categoria de Tamanho</h3>
                    <img src="data:image/png;base64,{charts[1]}" alt="Fix Ratio por Categoria">
                </div>
                
                <div class="chart">
                    <h3>Distribuição de Tamanhos de Métodos</h3>
                    <img src="data:image/png;base64,{charts[2]}" alt="Distribuição de Tamanhos">
                </div>
                
                <div class="chart">
                    <h3>Fix Ratio Médio por Repositório</h3>
                    <img src="data:image/png;base64,{charts[3]}" alt="Fix Ratio por Repositório">
                </div>
"""

        # Adicionar gráficos de complexidade ciclomática se disponíveis
        if len(charts) > 4 and "avg_complexity" in stats:
            html_content += f"""
                <h2 style="color: #667eea; margin-top: 50px; padding-top: 30px; border-top: 2px solid #eee;">Análise de Complexidade Ciclomática</h2>
                
                <div class="chart">
                    <h3>Complexidade Ciclomática vs Fix Ratio</h3>
                    <img src="data:image/png;base64,{charts[4]}" alt="Complexidade vs Fix Ratio">
                    <p style="margin-top: 10px; color: #666; font-size: 0.9em;">
                        Pontos coloridos pelo tamanho do método. Métodos mais complexos tendem a ter mais bugs?
                    </p>
                </div>
                
                <div class="chart">
                    <h3>Fix Ratio por Categoria de Complexidade</h3>
                    <img src="data:image/png;base64,{charts[5]}" alt="Fix Ratio por Complexidade">
                </div>
                
                <div class="chart">
                    <h3>Distribuição de Complexidade Ciclomática</h3>
                    <img src="data:image/png;base64,{charts[6]}" alt="Distribuição de Complexidade">
                </div>
                
                <div class="chart">
                    <h3>Tamanho vs Complexidade (colorido por Fix Ratio)</h3>
                    <img src="data:image/png;base64,{charts[7]}" alt="Tamanho vs Complexidade">
                    <p style="margin-top: 10px; color: #666; font-size: 0.9em;">
                        Vermelho indica maior fix ratio. Métodos grandes E complexos são mais problemáticos?
                    </p>
                </div>
"""

        html_content += """
            </div>
            
            <div class="section">
                <h2>Análise por Categoria de Tamanho</h2>
                <div class="category-stats">
                    <div class="category-card">
                        <h4>Métodos Pequenos (≤10 linhas)</h4>
                        <p><strong>Quantidade:</strong> {stats.get("size_categories", {}).get("small", 0)}</p>
                        <p><strong>Fix Ratio Médio:</strong> {stats.get("small_avg_fix_ratio", 0):.2%}</p>
                    </div>
                    <div class="category-card">
                        <h4>Métodos Médios (11-50 linhas)</h4>
                        <p><strong>Quantidade:</strong> {stats.get("size_categories", {}).get("medium", 0)}</p>
                        <p><strong>Fix Ratio Médio:</strong> {stats.get("medium_avg_fix_ratio", 0):.2%}</p>
                    </div>
                    <div class="category-card">
                        <h4>Métodos Grandes (>50 linhas)</h4>
                        <p><strong>Quantidade:</strong> {stats.get("size_categories", {}).get("large", 0)}</p>
                        <p><strong>Fix Ratio Médio:</strong> {stats.get("large_avg_fix_ratio", 0):.2%}</p>
                    </div>
                </div>
            </div>
"""

        # Adicionar seção de análise por complexidade ciclomática se disponível
        if "avg_complexity" in stats:
            html_content += f"""
            <div class="section">
                <h2>Análise por Complexidade Ciclomática</h2>
                
                <div class="stats-grid" style="margin-bottom: 30px;">
                    <div class="stat-card">
                        <h3>Complexidade Média</h3>
                        <div class="value">{stats.get("avg_complexity", 0):.1f}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Complexidade Mediana</h3>
                        <div class="value">{stats.get("median_complexity", 0):.0f}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Complexidade Máxima</h3>
                        <div class="value">{stats.get("max_complexity", 0):.0f}</div>
                    </div>
                </div>
                
                <div class="category-stats">
                    <div class="category-card">
                        <h4>Complexidade Baixa (≤5)</h4>
                        <p><strong>Quantidade:</strong> {stats.get("complexity_categories", {}).get("low", 0)}</p>
                        <p><strong>Fix Ratio Médio:</strong> {stats.get("complexity_low_avg_fix_ratio", 0):.2%}</p>
                    </div>
                    <div class="category-card">
                        <h4>Complexidade Média (6-10)</h4>
                        <p><strong>Quantidade:</strong> {stats.get("complexity_categories", {}).get("medium", 0)}</p>
                        <p><strong>Fix Ratio Médio:</strong> {stats.get("complexity_medium_avg_fix_ratio", 0):.2%}</p>
                    </div>
                    <div class="category-card">
                        <h4>Complexidade Alta (>10)</h4>
                        <p><strong>Quantidade:</strong> {stats.get("complexity_categories", {}).get("high", 0)}</p>
                        <p><strong>Fix Ratio Médio:</strong> {stats.get("complexity_high_avg_fix_ratio", 0):.2%}</p>
                    </div>
                </div>
            </div>
"""

        html_content += """
            <div class="section">
                <h2>Top 10 Métodos com Maior Fix Ratio</h2>
                <div class="method-list">
{top_methods_html}
                </div>
            </div>
            
            <div class="section">
                <h2>Conclusões</h2>
                <p>Esta análise revela a relação entre o tamanho dos métodos e a frequência de commits de fix. 
                Os resultados podem ajudar a entender se métodos maiores tendem a ter mais bugs ou se 
                métodos menores são mais propensos a mudanças.</p>
                
                <p style="margin-top: 15px;">Com base nos dados analisados, observamos que:</p>
                <ul style="margin-left: 20px; margin-top: 10px;">
                    <li>O tamanho médio dos métodos é de <strong>{stats.get("avg_method_size", 0):.1f} linhas</strong></li>
                    <li><strong>{stats.get("methods_with_fixes", 0)}</strong> métodos de um total de <strong>{stats.get("total_methods", 0)}</strong> tiveram commits de fix</li>
                    <li>A proporção média de commits de fix é de <strong>{stats.get("avg_fix_ratio", 0):.2%}</strong></li>
"""

        # Adicionar observações sobre complexidade se disponível
        if "avg_complexity" in stats:
            html_content += f"""
                    <li>A complexidade ciclomática média é de <strong>{stats.get("avg_complexity", 0):.1f}</strong></li>
                    <li>Métodos com complexidade alta (>10) representam <strong>{stats.get("complexity_categories", {}).get("high", 0)}</strong> do total</li>
"""
            
            # Análise comparativa se houver dados suficientes
            low_fix = stats.get("complexity_low_avg_fix_ratio", 0)
            high_fix = stats.get("complexity_high_avg_fix_ratio", 0)
            if low_fix > 0 and high_fix > 0:
                ratio_diff = (high_fix / low_fix - 1) * 100 if low_fix > 0 else 0
                if ratio_diff > 10:
                    html_content += f"""
                    <li>⚠️ Métodos com alta complexidade têm <strong>{ratio_diff:.0f}% mais</strong> commits de fix em relação aos de baixa complexidade</li>
"""
                elif ratio_diff < -10:
                    html_content += f"""
                    <li>✅ Métodos com baixa complexidade têm <strong>{abs(ratio_diff):.0f}% mais</strong> commits de fix em relação aos de alta complexidade</li>
"""

        html_content += """
                </ul>
            </div>
            
            <div class="methodology">
                <h3>Metodologia</h3>
                <ul>
                    <li>Utilizou-se o <strong>CodeShovel</strong> para análise de histórico de métodos</li>
                    <li>Commits de fix foram identificados por palavras-chave: <em>fix, bug, issue, problem, error</em></li>
                    <li>Métodos foram categorizados por tamanho: pequeno (≤10), médio (11-50), grande (>50)</li>
"""

        if "avg_complexity" in stats:
            html_content += """
                    <li>Complexidade ciclomática calculada analisando estruturas de controle (if, for, while, switch, etc.)</li>
                    <li>Categorias de complexidade: baixa (≤5), média (6-10), alta (>10)</li>
"""

        html_content += """
                    <li>Análise focou em repositórios Java de código aberto</li>
                </ul>
            </div>
        </div>
        
        <footer>
            Relatório gerado automaticamente pelo CodeShovel Fix Analysis Tool
        </footer>
    </div>
</body>
</html>
"""
        return html_content

