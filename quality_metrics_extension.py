#!/usr/bin/env python3
"""
Extensões de Qualidade de Código para CodeShovel Fix Analysis Tool

Este módulo adiciona métricas de qualidade de código que o CodeShovel não fornece:
1. Contagem de linhas excluindo comentários
2. Cálculo de complexidade ciclomática
3. Análise de tamanho dos identificadores
4. Análise de autores dos commits de fix
"""

import re
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class QualityMetrics:
    """Métricas de qualidade de código"""
    
    code_lines_no_comments: int
    total_lines_with_comments: int
    comment_ratio: float
    cyclomatic_complexity: int
    identifier_stats: Dict[str, float]
    commit_authors: List[str]
    author_concentration: float
    complexity_evolution: Optional[Dict[str, int]] = None

@dataclass
class EnhancedMethodInfo:
    """Informações expandidas sobre um método"""
    
    # Dados originais do CodeShovel
    name: str
    file_path: str
    start_line: int
    end_line: int
    size_lines: int
    repository: str
    commit_count: int
    fix_commit_count: int
    fix_ratio: float
    
    # Novas métricas de qualidade
    quality_metrics: QualityMetrics

class CodeQualityAnalyzer:
    """Analisador de qualidade de código"""
    
    def __init__(self, repositories_dir: str):
        self.repositories_dir = Path(repositories_dir)
    
    def count_code_lines_excluding_comments(self, source_code: str) -> Tuple[int, int, float]:
        """
        Conta linhas de código excluindo comentários
        
        Returns:
            (linhas_sem_comentarios, linhas_totais, razao_comentarios)
        """
        lines = source_code.split('\n')
        code_lines = []
        total_lines = len([line for line in lines if line.strip()])
        
        in_block_comment = False
        
        for line in lines:
            line = line.strip()
            
            # Pular linhas vazias
            if not line:
                continue
                
            # Comentário de linha única
            if line.startswith('//'):
                continue
                
            # Comentário de bloco na mesma linha
            if '/*' in line and '*/' in line:
                # Remove o comentário e verifica se sobra código
                cleaned = re.sub(r'/\*.*?\*/', '', line).strip()
                if cleaned:
                    code_lines.append(cleaned)
                continue
                
            # Início de comentário de bloco
            if '/*' in line:
                in_block_comment = True
                # Verifica se há código antes do comentário
                before_comment = line[:line.find('/*')].strip()
                if before_comment:
                    code_lines.append(before_comment)
                continue
                
            # Fim de comentário de bloco
            if '*/' in line:
                in_block_comment = False
                # Verifica se há código após o comentário
                after_comment = line[line.find('*/') + 2:].strip()
                if after_comment:
                    code_lines.append(after_comment)
                continue
                
            # Linha dentro de comentário de bloco
            if in_block_comment:
                continue
                
            # Linha de código normal
            code_lines.append(line)
        
        code_line_count = len(code_lines)
        comment_ratio = (total_lines - code_line_count) / total_lines if total_lines > 0 else 0
        
        return code_line_count, total_lines, comment_ratio
    
    def calculate_cyclomatic_complexity(self, source_code: str) -> int:
        """
        Calcula complexidade ciclomática
        CC = 1 + número de pontos de decisão
        """
        complexity = 1  # Complexidade base
        
        # Palavras-chave que aumentam complexidade
        decision_keywords = [
            r'\bif\b', r'\belse\s+if\b', r'\bwhile\b', r'\bfor\b', 
            r'\bswitch\b', r'\bcase\b', r'\bcatch\b', r'\b\?\s*:', 
            r'\&\&', r'\|\|'
        ]
        
        for keyword_pattern in decision_keywords:
            matches = re.findall(keyword_pattern, source_code, re.IGNORECASE)
            complexity += len(matches)
            
        return complexity
    
    def analyze_identifiers(self, source_code: str) -> Dict[str, float]:
        """
        Analisa tamanho e características dos identificadores
        """
        # Extrair identificadores (variáveis, métodos, classes)
        identifier_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
        identifiers = re.findall(identifier_pattern, source_code)
        
        # Filtrar palavras-chave Java
        java_keywords = {
            'public', 'private', 'protected', 'static', 'final', 'abstract',
            'class', 'interface', 'extends', 'implements', 'import', 'package',
            'if', 'else', 'while', 'for', 'switch', 'case', 'default',
            'try', 'catch', 'finally', 'throw', 'throws', 'return',
            'int', 'double', 'float', 'boolean', 'char', 'String', 'void',
            'this', 'super', 'new', 'null', 'true', 'false'
        }
        
        filtered_identifiers = [id for id in identifiers if id.lower() not in java_keywords]
        
        if not filtered_identifiers:
            return {
                'avg_length': 0.0,
                'min_length': 0.0,
                'max_length': 0.0,
                'total_count': 0,
                'short_names_ratio': 0.0  # Proporção de nomes com <= 3 caracteres
            }
        
        lengths = [len(identifier) for identifier in filtered_identifiers]
        short_names = [l for l in lengths if l <= 3]
        
        return {
            'avg_length': sum(lengths) / len(lengths),
            'min_length': float(min(lengths)),
            'max_length': float(max(lengths)),
            'total_count': len(filtered_identifiers),
            'short_names_ratio': len(short_names) / len(lengths)
        }
    
    def get_commit_authors_for_method(self, repo_path: Path, file_path: str, 
                                    start_line: int, end_line: int) -> List[str]:
        """
        Obtém autores dos commits que modificaram um método específico
        """
        try:
            # Usar git blame para obter autores por linha
            cmd = [
                'git', 'blame', '--line-porcelain', 
                f'-L{start_line},{end_line}', file_path
            ]
            
            result = subprocess.run(
                cmd, cwd=repo_path, capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                logger.warning(f"Git blame falhou para {file_path}: {result.stderr}")
                return []
            
            authors = []
            for line in result.stdout.split('\n'):
                if line.startswith('author '):
                    author = line[7:].strip()  # Remove 'author '
                    if author not in authors:
                        authors.append(author)
            
            return authors
            
        except Exception as e:
            logger.error(f"Erro ao obter autores para {file_path}: {e}")
            return []
    
    def get_fix_commit_authors(self, repo_path: Path, file_path: str) -> List[str]:
        """
        Obtém autores específicos dos commits de fix para um arquivo
        """
        try:
            # Buscar commits de fix para o arquivo específico
            fix_keywords = ['fix', 'bug', 'issue', 'problem', 'error', 'hotfix', 'patch']
            grep_pattern = '|'.join(fix_keywords)
            
            cmd = [
                'git', 'log', '--pretty=format:%an', 
                f'--grep={grep_pattern}', '-i', '--', file_path
            ]
            
            result = subprocess.run(
                cmd, cwd=repo_path, capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                return []
            
            authors = [author.strip() for author in result.stdout.split('\n') if author.strip()]
            return list(set(authors))  # Remove duplicatas
            
        except Exception as e:
            logger.error(f"Erro ao obter autores de fix para {file_path}: {e}")
            return []
    
    def calculate_author_concentration(self, authors: List[str]) -> float:
        """
        Calcula concentração de autores (Gini coefficient simplificado)
        """
        if not authors:
            return 0.0
        
        # Contar frequência de cada autor
        author_counts = {}
        for author in authors:
            author_counts[author] = author_counts.get(author, 0) + 1
        
        # Calcular concentração (% do autor mais frequente)
        max_count = max(author_counts.values())
        total_count = len(authors)
        
        return max_count / total_count
    
    def get_method_source_code(self, file_path: Path, start_line: int, end_line: int) -> str:
        """
        Extrai o código fonte de um método específico
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Ajustar para índices baseados em 0
            start_idx = max(0, start_line - 1)
            end_idx = min(len(lines), end_line)
            
            return ''.join(lines[start_idx:end_idx])
            
        except Exception as e:
            logger.error(f"Erro ao ler código fonte de {file_path}: {e}")
            return ""
    
    def analyze_method_quality(self, repo_path: Path, file_path: str, 
                             start_line: int, end_line: int) -> QualityMetrics:
        """
        Analisa todas as métricas de qualidade para um método
        """
        full_file_path = repo_path / file_path
        source_code = self.get_method_source_code(full_file_path, start_line, end_line)
        
        if not source_code:
            return QualityMetrics(
                code_lines_no_comments=0,
                total_lines_with_comments=0,
                comment_ratio=0.0,
                cyclomatic_complexity=1,
                identifier_stats={},
                commit_authors=[],
                author_concentration=0.0
            )
        
        # 1. Análise de linhas e comentários
        code_lines, total_lines, comment_ratio = self.count_code_lines_excluding_comments(source_code)
        
        # 2. Complexidade ciclomática
        complexity = self.calculate_cyclomatic_complexity(source_code)
        
        # 3. Análise de identificadores
        identifier_stats = self.analyze_identifiers(source_code)
        
        # 4. Análise de autores
        commit_authors = self.get_commit_authors_for_method(repo_path, file_path, start_line, end_line)
        fix_authors = self.get_fix_commit_authors(repo_path, file_path)
        author_concentration = self.calculate_author_concentration(fix_authors)
        
        return QualityMetrics(
            code_lines_no_comments=code_lines,
            total_lines_with_comments=total_lines,
            comment_ratio=comment_ratio,
            cyclomatic_complexity=complexity,
            identifier_stats=identifier_stats,
            commit_authors=commit_authors,
            author_concentration=author_concentration
        )

def enhance_method_info(original_method_info, quality_metrics: QualityMetrics) -> EnhancedMethodInfo:
    """
    Cria uma versão expandida do MethodInfo com métricas de qualidade
    """
    return EnhancedMethodInfo(
        name=original_method_info.name,
        file_path=original_method_info.file_path,
        start_line=original_method_info.start_line,
        end_line=original_method_info.end_line,
        size_lines=original_method_info.size_lines,
        repository=original_method_info.repository,
        commit_count=original_method_info.commit_count,
        fix_commit_count=original_method_info.fix_commit_count,
        fix_ratio=original_method_info.fix_ratio,
        quality_metrics=quality_metrics
    ) 

def serialize_enhanced_method_info(enhanced_method_info: EnhancedMethodInfo) -> Dict:
    """Converte EnhancedMethodInfo para dicionário serializável"""
    return {
        "name": enhanced_method_info.name,
        "file_path": enhanced_method_info.file_path,
        "start_line": enhanced_method_info.start_line,
        "end_line": enhanced_method_info.end_line,
        "size_lines": enhanced_method_info.size_lines,
        "repository": enhanced_method_info.repository,
        "commit_count": enhanced_method_info.commit_count,
        "fix_commit_count": enhanced_method_info.fix_commit_count,
        "fix_ratio": enhanced_method_info.fix_ratio,
        "quality_metrics": {
            "code_lines_no_comments": enhanced_method_info.quality_metrics.code_lines_no_comments,
            "total_lines_with_comments": enhanced_method_info.quality_metrics.total_lines_with_comments,
            "comment_ratio": enhanced_method_info.quality_metrics.comment_ratio,
            "cyclomatic_complexity": enhanced_method_info.quality_metrics.cyclomatic_complexity,
            "identifier_stats": enhanced_method_info.quality_metrics.identifier_stats,
            "commit_authors": enhanced_method_info.quality_metrics.commit_authors,
            "author_concentration": enhanced_method_info.quality_metrics.author_concentration,
            "complexity_evolution": enhanced_method_info.quality_metrics.complexity_evolution
        }
    } 