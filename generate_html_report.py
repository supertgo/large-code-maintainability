#!/usr/bin/env python3
"""
Script para gerar relatório HTML a partir de resultados salvos

Uso:
    python generate_html_report.py [--results-dir path/to/results]
"""

import argparse
import sys
from pathlib import Path
from fix_analysis import CodeShovelAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description="Gera relatório HTML a partir de resultados salvos"
    )
    parser.add_argument(
        "--results-dir",
        default="./fix_analysis_results",
        help="Diretório contendo os resultados JSON (padrão: ./fix_analysis_results)",
    )
    parser.add_argument(
        "--codeshovel-jar",
        default="./codeshovel.jar",
        help="Caminho para o JAR do CodeShovel (padrão: ./codeshovel.jar)",
    )

    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"❌ Diretório não encontrado: {results_dir}")
        print("Execute a análise primeiro antes de gerar o HTML.")
        return 1

    # Verificar se existem arquivos de resultado
    json_files = list(results_dir.glob("*_fix_analysis.json"))
    if not json_files:
        print(f"❌ Nenhum arquivo de resultado encontrado em: {results_dir}")
        print("Execute a análise primeiro antes de gerar o HTML.")
        return 1

    print(f"📊 Encontrados {len(json_files)} arquivos de resultado")
    print(f"📂 Diretório: {results_dir}")
    print("\n🔄 Gerando relatório HTML...")

    try:
        # Criar analisador - passando results_dir como terceiro parâmetro
        analyzer = CodeShovelAnalyzer(
            args.codeshovel_jar, 
            str(results_dir),
            results_dir=str(results_dir)
        )

        # Gerar relatório HTML
        html_file = analyzer.generate_html_report()

        if html_file:
            print(f"\n✅ Relatório HTML gerado com sucesso!")
            print(f"📄 Arquivo: {html_file}")
            print(f"\n🌐 Abra o arquivo no navegador para visualizar o relatório.")
        else:
            print("\n⚠️  Não foi possível gerar o relatório HTML")
            return 1

    except Exception as e:
        print(f"\n❌ Erro ao gerar relatório: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
