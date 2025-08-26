#!/usr/bin/env python3
"""
Script de execução simplificado para análise de fix vs tamanho de métodos

Uso:
    python run_analysis.py --codeshovel-jar path/to/codeshovel.jar --repositories-dir path/to/repos
"""

import os
import sys
from pathlib import Path
from fix_analysis import CodeShovelAnalyzer, main

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    try:
        import pandas
        import matplotlib
        import seaborn
        import numpy
        print("✓ Todas as dependências estão instaladas")
        return True
    except ImportError as e:
        print(f"✗ Dependência faltando: {e}")
        print("Execute: pip install -r requirements.txt")
        return False

def check_codeshovel_jar(jar_path):
    """Verifica se o JAR do CodeShovel existe"""
    if not os.path.exists(jar_path):
        print(f"✗ JAR do CodeShovel não encontrado: {jar_path}")
        print("Certifique-se de que o caminho está correto")
        return False
    
    print(f"✓ JAR do CodeShovel encontrado: {jar_path}")
    return True

def check_repositories_dir(repos_dir):
    """Verifica se o diretório de repositórios existe e contém repositórios"""
    repos_path = Path(repos_dir)
    if not repos_path.exists():
        print(f"✗ Diretório de repositórios não encontrado: {repos_dir}")
        return False
    
    # Verificar se há repositórios Git
    git_repos = [d for d in repos_path.iterdir() if d.is_dir() and (d / '.git').exists()]
    
    if not git_repos:
        print(f"✗ Nenhum repositório Git encontrado em: {repos_dir}")
        print("Execute o script de clonagem primeiro:")
        print(f"  bash bin/clone-java-repositories.sh {repos_dir}")
        return False
    
    print(f"✓ {len(git_repos)} repositórios Git encontrados em: {repos_dir}")
    return True

def main_wrapper():
    """Wrapper principal com verificações"""
    print("🔍 CodeShovel Fix Analysis Tool")
    print("=" * 50)
    
    # Verificar dependências
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar argumentos
    if len(sys.argv) < 3:
        print("\nUso:")
        print("  python run_analysis.py --codeshovel-jar <jar_path> --repositories-dir <repos_dir>")
        print("\nExemplo:")
        print("  python run_analysis.py --codeshovel-jar codeshovel.jar --repositories-dir ./repos")
        print("\nOpções:")
        print("  --repo-limit <num>     Limite de repositórios (padrão: 5)")
        print("  --method-limit <num>   Limite de métodos por repo (padrão: 50)")
        sys.exit(1)
    
    # Extrair argumentos
    args = sys.argv[1:]
    jar_path = None
    repos_dir = None
    repo_limit = 5
    method_limit = 50
    
    i = 0
    while i < len(args):
        if args[i] == '--codeshovel-jar' and i + 1 < len(args):
            jar_path = args[i + 1]
            i += 2
        elif args[i] == '--repositories-dir' and i + 1 < len(args):
            repos_dir = args[i + 1]
            i += 2
        elif args[i] == '--repo-limit' and i + 1 < len(args):
            repo_limit = int(args[i + 1])
            i += 2
        elif args[i] == '--method-limit' and i + 1 < len(args):
            method_limit = int(args[i + 1])
            i += 2
        else:
            i += 1
    
    if not jar_path or not repos_dir:
        print("✗ Argumentos obrigatórios não fornecidos")
        sys.exit(1)
    
    # Verificações
    if not check_codeshovel_jar(jar_path):
        sys.exit(1)
    
    if not check_repositories_dir(repos_dir):
        sys.exit(1)
    
    print("\n🚀 Iniciando análise...")
    print("=" * 50)
    
    # Executar análise
    try:
        # Simular argumentos para o argparse
        sys.argv = [
            'fix_analysis.py',
            '--codeshovel-jar', jar_path,
            '--repositories-dir', repos_dir,
            '--repo-limit', str(repo_limit),
            '--method-limit', str(method_limit)
        ]
        
        main()
        
    except KeyboardInterrupt:
        print("\n⚠️  Análise interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main_wrapper() 