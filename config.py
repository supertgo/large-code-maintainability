#!/usr/bin/env python3
"""
Arquivo de configuração para CodeShovel Fix Analysis Tool

Este arquivo centraliza todas as configurações da ferramenta,
permitindo fácil personalização sem modificar o código principal.
"""

import os
from pathlib import Path

# ============================================================================
# CONFIGURAÇÕES PRINCIPAIS
# ============================================================================

# Caminhos padrão
DEFAULT_CODESHOVEL_JAR = "codeshovel.jar"
DEFAULT_REPOSITORIES_DIR = "./repos"
DEFAULT_RESULTS_DIR = "./fix_analysis_results"

# Limites padrão
DEFAULT_REPO_LIMIT = 5
DEFAULT_METHOD_LIMIT = 50

# Timeout para execução do CodeShovel (em segundos)
CODESHOVEL_TIMEOUT = 300

# ============================================================================
# CONFIGURAÇÕES DE ANÁLISE
# ============================================================================

# Palavras-chave para identificar commits de fix
FIX_KEYWORDS = [
    "fix",
    "bug",
    "issue",
    "problem", 
    "error",
    "bugfix",
    "hotfix",
    "patch",
    "resolve",
    "correct",
    "repair",
    "debug"
]

# Categorias de tamanho de método (em linhas)
METHOD_SIZE_CATEGORIES = {
    "small": (0, 10),      # Pequeno: 1-10 linhas
    "medium": (11, 50),    # Médio: 11-50 linhas
    "large": (51, float('inf'))  # Grande: 51+ linhas
}

# ============================================================================
# CONFIGURAÇÕES DE VISUALIZAÇÃO
# ============================================================================

# Configurações de gráficos
PLOT_CONFIG = {
    "figure_size": (15, 12),
    "dpi": 300,
    "style": "seaborn-v0_8",
    "save_format": "png"
}

# Cores para categorias de tamanho
SIZE_COLORS = {
    "small": "#2E8B57",    # Verde escuro
    "medium": "#FF8C00",   # Laranja escuro
    "large": "#DC143C"     # Vermelho escuro
}

# ============================================================================
# CONFIGURAÇÕES DE LOGGING
# ============================================================================

# Nível de logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Arquivo de log
LOG_FILE = "fix_analysis.log"

# ============================================================================
# CONFIGURAÇÕES DE EXPORTAÇÃO
# ============================================================================

# Formatos de exportação suportados
EXPORT_FORMATS = ["csv", "json", "xlsx"]

# Configurações de CSV
CSV_CONFIG = {
    "encoding": "utf-8",
    "index": False,
    "date_format": "%Y-%m-%d %H:%M:%S"
}

# Configurações de Excel
EXCEL_CONFIG = {
    "sheet_name": "Fix Analysis",
    "index": False,
    "engine": "openpyxl"
}

# ============================================================================
# CONFIGURAÇÕES DE FILTROS
# ============================================================================

# Filtros para métodos
METHOD_FILTERS = {
    "min_size": 1,           # Tamanho mínimo (linhas)
    "max_size": 1000,        # Tamanho máximo (linhas)
    "min_commits": 1,        # Número mínimo de commits
    "exclude_test_files": True,  # Excluir arquivos de teste
    "exclude_build_files": True  # Excluir arquivos de build
}

# Padrões para excluir arquivos
EXCLUDE_PATTERNS = [
    "test", "Test", "TEST",
    "target", "build", "out",
    ".git", "node_modules",
    "*.class", "*.jar", "*.war"
]

# ============================================================================
# FUNÇÕES DE CONFIGURAÇÃO
# ============================================================================

def get_config_value(key, default=None):
    """
    Obtém valor de configuração, priorizando variáveis de ambiente
    
    Args:
        key: Chave da configuração
        default: Valor padrão se não encontrado
        
    Returns:
        Valor da configuração
    """
    # Tentar variável de ambiente primeiro
    env_key = f"CODESHOVEL_{key.upper()}"
    if env_key in os.environ:
        return os.environ[env_key]
    
    # Retornar valor padrão
    return globals().get(key, default)

def get_codeshovel_jar():
    """Obtém caminho para o JAR do CodeShovel"""
    return get_config_value("DEFAULT_CODESHOVEL_JAR")

def get_repositories_dir():
    """Obtém diretório de repositórios"""
    return get_config_value("DEFAULT_REPOSITORIES_DIR")

def get_results_dir():
    """Obtém diretório de resultados"""
    return get_config_value("DEFAULT_RESULTS_DIR")

def get_fix_keywords():
    """Obtém lista de palavras-chave para fix"""
    return FIX_KEYWORDS.copy()

def get_method_size_categories():
    """Obtém categorias de tamanho de método"""
    return METHOD_SIZE_CATEGORIES.copy()

def get_plot_config():
    """Obtém configurações de gráficos"""
    return PLOT_CONFIG.copy()

def get_method_filters():
    """Obtém filtros para métodos"""
    return METHOD_FILTERS.copy()

def get_exclude_patterns():
    """Obtém padrões de exclusão"""
    return EXCLUDE_PATTERNS.copy()

def get_example_repositories():
    """Obtém repositórios de exemplo"""
    return EXAMPLE_REPOSITORIES.copy()

# ============================================================================
# VALIDAÇÃO DE CONFIGURAÇÃO
# ============================================================================

def validate_config():
    """
    Valida as configurações da ferramenta
    
    Returns:
        Lista de problemas encontrados
    """
    problems = []
    
    # Verificar se o JAR existe
    jar_path = get_codeshovel_jar()
    if not os.path.exists(jar_path):
        problems.append(f"CodeShovel JAR não encontrado: {jar_path}")
    
    # Verificar se o diretório de repositórios existe
    repos_dir = get_repositories_dir()
    if not os.path.exists(repos_dir):
        problems.append(f"Diretório de repositórios não existe: {repos_dir}")
    
    # Verificar se há repositórios Git
    if os.path.exists(repos_dir):
        repos_path = Path(repos_dir)
        git_repos = [d for d in repos_path.iterdir() if d.is_dir() and (d / '.git').exists()]
        if not git_repos:
            problems.append(f"Nenhum repositório Git encontrado em: {repos_dir}")
    
    # Verificar configurações de tamanho
    size_cats = get_method_size_categories()
    if len(size_cats) < 2:
        problems.append("Pelo menos 2 categorias de tamanho são necessárias")
    
    # Verificar palavras-chave
    keywords = get_fix_keywords()
    if not keywords:
        problems.append("Pelo menos uma palavra-chave de fix é necessária")
    
    return problems

def print_config_summary():
    """Imprime resumo das configurações"""
    print("🔧 Configuração da Ferramenta")
    print("=" * 40)
    
    print(f"CodeShovel JAR: {get_codeshovel_jar()}")
    print(f"Diretório de repositórios: {get_repositories_dir()}")
    print(f"Diretório de resultados: {get_results_dir()}")
    print(f"Limite de repositórios: {get_config_value('DEFAULT_REPO_LIMIT')}")
    print(f"Limite de métodos: {get_config_value('DEFAULT_METHOD_LIMIT')}")
    print(f"Timeout CodeShovel: {get_config_value('CODESHOVEL_TIMEOUT')}s")
    
    print(f"\nPalavras-chave de fix: {', '.join(get_fix_keywords())}")
    print(f"Categorias de tamanho: {list(get_method_size_categories().keys())}")
    
    # Verificar problemas
    problems = validate_config()
    if problems:
        print(f"\n⚠️  Problemas encontrados:")
        for problem in problems:
            print(f"  - {problem}")
    else:
        print(f"\n✅ Configuração válida")

if __name__ == "__main__":
    print_config_summary() 