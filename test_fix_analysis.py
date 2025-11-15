#!/usr/bin/env python3
"""
Testes unitários para o CodeShovel Fix Analysis Tool

Este módulo contém testes para as principais funcionalidades da ferramenta,
incluindo extração de métodos, análise de commits e geração de relatórios.
"""

import unittest
import os
import json
import tempfile
import shutil
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Mock matplotlib antes de importar para evitar problemas
sys.modules['matplotlib'] = MagicMock()
sys.modules['matplotlib.pyplot'] = MagicMock()

# Importar módulos a serem testados
from fix_analysis import (
    CodeShovelAnalyzer,
    MethodInfo,
    FixAnalysis,
)
from quality_metrics_extension import (
    CodeQualityAnalyzer,
    QualityMetrics,
)


class TestCodeShovelAnalyzer(unittest.TestCase):
    """Testes para a classe CodeShovelAnalyzer"""

    def setUp(self):
        """Configuração antes de cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.codeshovel_jar = os.path.join(self.temp_dir, "codeshovel.jar")
        
        # Criar arquivo JAR falso
        with open(self.codeshovel_jar, "w") as f:
            f.write("fake jar")
        
        self.repos_dir = os.path.join(self.temp_dir, "repos")
        os.makedirs(self.repos_dir, exist_ok=True)
        
        self.analyzer = CodeShovelAnalyzer(self.codeshovel_jar, self.repos_dir)

    def tearDown(self):
        """Limpeza após cada teste"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_analyzer_initialization(self):
        """Teste 1: Verifica inicialização do analisador"""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(self.analyzer.codeshovel_jar_path, self.codeshovel_jar)
        self.assertEqual(self.analyzer.repositories_dir, Path(self.repos_dir))
        self.assertTrue(self.analyzer.results_dir.exists())

    def test_02_analyzer_initialization_missing_jar(self):
        """Teste 2: Verifica erro quando JAR não existe"""
        with self.assertRaises(FileNotFoundError):
            CodeShovelAnalyzer("/invalid/path/to.jar", self.repos_dir)

    def test_03_find_java_files(self):
        """Teste 3: Verifica busca de arquivos Java"""
        # Criar estrutura de diretórios (sem "test" no nome)
        repo_path = Path(self.repos_dir) / "sample_repo"
        repo_path.mkdir(exist_ok=True)
        
        # Criar arquivos Java com conteúdo
        with open(repo_path / "Main.java", "w") as f:
            f.write("public class Main {}")
        with open(repo_path / "Utils.java", "w") as f:
            f.write("public class Utils {}")
        
        # Criar arquivo de teste (deve ser ignorado)
        test_dir = repo_path / "tests"
        test_dir.mkdir(exist_ok=True)
        with open(test_dir / "TestMain.java", "w") as f:
            f.write("public class TestMain {}")
        
        java_files = self.analyzer.find_java_files(repo_path)
        
        self.assertEqual(len(java_files), 2)
        self.assertTrue(any("Main.java" in str(f) for f in java_files))
        self.assertFalse(any("TestMain.java" in str(f) for f in java_files))

    def test_04_extract_methods_from_file(self):
        """Teste 4: Verifica extração de métodos de arquivo Java"""
        # Criar arquivo Java de exemplo
        java_content = """
public class Example {
    public void method1() {
        System.out.println("Method 1");
    }
    
    private int method2(String param) {
        return param.length();
    }
}
"""
        java_file = Path(self.temp_dir) / "Example.java"
        with open(java_file, "w") as f:
            f.write(java_content)
        
        methods = self.analyzer.extract_methods_from_file(java_file)
        
        self.assertGreater(len(methods), 0)
        # Verificar que métodos foram extraídos
        method_names = [m[0] for m in methods]
        self.assertIn("method1", method_names)

    def test_05_analyze_fix_commits_valid_data(self):
        """Teste 5: Verifica análise de commits de fix com dados válidos"""
        codeshovel_data = {
            "changeHistoryDetails": {
                "abc123": {
                    "commitMessage": "fix: corrected bug in method"
                },
                "def456": {
                    "commitMessage": "added new feature"
                },
                "ghi789": {
                    "commitMessage": "bugfix: resolved issue #123"
                }
            }
        }
        
        total_commits, fix_commits = self.analyzer.analyze_fix_commits(codeshovel_data)
        
        self.assertEqual(total_commits, 3)
        self.assertEqual(len(fix_commits), 2)

    def test_06_analyze_fix_commits_invalid_data(self):
        """Teste 6: Verifica análise de commits com dados inválidos"""
        # Testar com None
        total, fixes = self.analyzer.analyze_fix_commits(None)
        self.assertEqual(total, 0)
        self.assertEqual(len(fixes), 0)
        
        # Testar com dicionário vazio
        total, fixes = self.analyzer.analyze_fix_commits({})
        self.assertEqual(total, 0)
        self.assertEqual(len(fixes), 0)

    def test_07_analyze_fix_commits_keywords(self):
        """Teste 7: Verifica detecção de palavras-chave em commits"""
        test_messages = [
            ("fix: bug corrected", True),
            ("bug: issue resolved", True),
            ("error: fixed problem", True),
            ("issue: resolved #123", True),
            ("problem: fixed", True),
            ("added new feature", False),
            ("refactor: improved code", False),
        ]
        
        for message, should_match in test_messages:
            codeshovel_data = {
                "changeHistoryDetails": {
                    "abc123": {"commitMessage": message}
                }
            }
            
            total, fixes = self.analyzer.analyze_fix_commits(codeshovel_data)
            
            if should_match:
                self.assertEqual(len(fixes), 1, f"Failed for message: {message}")
            else:
                self.assertEqual(len(fixes), 0, f"Failed for message: {message}")

    def test_08_generate_statistics_empty(self):
        """Teste 8: Verifica estatísticas com dados vazios"""
        stats = self.analyzer.generate_statistics([])
        self.assertEqual(stats, {})

    def test_09_generate_statistics_valid(self):
        """Teste 9: Verifica geração de estatísticas com dados válidos"""
        # Criar análises de teste
        from quality_metrics_extension import EnhancedMethodInfo, QualityMetrics
        
        analyses = []
        for i in range(5):
            quality_metrics = QualityMetrics(
                cyclomatic_complexity=i + 1,
                code_lines_no_comments=10 * (i + 1),
                total_lines_with_comments=15 * (i + 1),
                comment_ratio=0.2,
                identifier_stats={
                    "avg_length": 8.0,
                    "min_length": 2.0,
                    "max_length": 15.0,
                    "total_count": 10,
                    "short_names_ratio": 0.1
                },
                commit_authors=["author1", "author2"],
                author_concentration=0.5
            )
            
            method_info = EnhancedMethodInfo(
                name=f"method{i}",
                file_path=f"file{i}.java",
                start_line=1,
                end_line=10,
                size_lines=10,
                repository="test_repo",
                commit_count=10,
                fix_commit_count=i,
                fix_ratio=i / 10.0,
                codeshovel_data={},
                quality_metrics=quality_metrics
            )
            
            analysis = FixAnalysis(
                method_info=method_info,
                fix_commits=[],
                total_changes=[]
            )
            analyses.append(analysis)
        
        stats = self.analyzer.generate_statistics(analyses)
        
        self.assertEqual(stats["total_methods"], 5)
        self.assertIn("avg_method_size", stats)
        self.assertIn("avg_fix_ratio", stats)

    def test_10_save_and_load_results(self):
        """Teste 10: Verifica salvamento e carregamento de resultados"""
        from quality_metrics_extension import EnhancedMethodInfo, QualityMetrics
        
        # Criar análise de teste
        quality_metrics = QualityMetrics(
            cyclomatic_complexity=2,
            code_lines_no_comments=20,
            total_lines_with_comments=25,
            comment_ratio=0.2,
            identifier_stats={
                "avg_length": 8.0,
                "min_length": 2.0,
                "max_length": 15.0,
                "total_count": 10,
                "short_names_ratio": 0.1
            },
            commit_authors=["author1"],
            author_concentration=1.0
        )
        
        method_info = EnhancedMethodInfo(
            name="testMethod",
            file_path="TestFile.java",
            start_line=1,
            end_line=10,
            size_lines=10,
            repository="test_repo",
            commit_count=5,
            fix_commit_count=2,
            fix_ratio=0.4,
            codeshovel_data={"test": "data"},
            quality_metrics=quality_metrics
        )
        
        analysis = FixAnalysis(
            method_info=method_info,
            fix_commits=[],
            total_changes=[]
        )
        
        # Salvar resultados
        self.analyzer.save_results("test_repo", [analysis])
        
        # Verificar que arquivo foi criado
        results_file = self.analyzer.results_dir / "test_repo_fix_analysis.json"
        self.assertTrue(results_file.exists())
        
        # Carregar e verificar conteúdo
        with open(results_file, "r") as f:
            data = json.load(f)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["method_info"]["name"], "testMethod")


class TestQualityMetrics(unittest.TestCase):
    """Testes para análise de métricas de qualidade"""

    def test_11_quality_metrics_creation(self):
        """Teste 11: Verifica criação de métricas de qualidade"""
        metrics = QualityMetrics(
            cyclomatic_complexity=5,
            code_lines_no_comments=100,
            total_lines_with_comments=120,
            comment_ratio=0.166,
            identifier_stats={
                "avg_length": 10.0,
                "min_length": 2.0,
                "max_length": 20.0,
                "total_count": 50,
                "short_names_ratio": 0.1
            },
            commit_authors=["author1", "author2", "author3"],
            author_concentration=0.33
        )
        
        self.assertEqual(metrics.cyclomatic_complexity, 5)
        self.assertEqual(metrics.code_lines_no_comments, 100)
        self.assertEqual(metrics.total_lines_with_comments, 120)
        self.assertAlmostEqual(metrics.comment_ratio, 0.166, places=3)
        self.assertEqual(len(metrics.commit_authors), 3)

    def test_12_quality_metrics_empty_authors(self):
        """Teste 12: Verifica métricas com lista vazia de autores"""
        metrics = QualityMetrics(
            cyclomatic_complexity=1,
            code_lines_no_comments=10,
            total_lines_with_comments=10,
            comment_ratio=0.0,
            identifier_stats={},
            commit_authors=[],
            author_concentration=0.0
        )
        
        self.assertEqual(len(metrics.commit_authors), 0)
        self.assertEqual(metrics.author_concentration, 0.0)


class TestDataProcessing(unittest.TestCase):
    """Testes para processamento de dados"""

    def test_13_dataframe_creation(self):
        """Teste 13: Verifica criação de DataFrame para análise"""
        data = [
            {
                "method_name": "method1",
                "repository": "repo1",
                "size_lines": 10,
                "commit_count": 5,
                "fix_commit_count": 2,
                "fix_ratio": 0.4
            },
            {
                "method_name": "method2",
                "repository": "repo2",
                "size_lines": 50,
                "commit_count": 10,
                "fix_commit_count": 3,
                "fix_ratio": 0.3
            }
        ]
        
        df = pd.DataFrame(data)
        
        self.assertEqual(len(df), 2)
        self.assertIn("method_name", df.columns)
        self.assertIn("fix_ratio", df.columns)

    def test_14_size_categorization(self):
        """Teste 14: Verifica categorização por tamanho"""
        data = {
            "size_lines": [5, 15, 100, 8, 45, 200]
        }
        df = pd.DataFrame(data)
        
        size_categories = pd.cut(
            df["size_lines"],
            bins=[0, 10, 50, float("inf")],
            labels=["small", "medium", "large"]
        )
        
        self.assertEqual(list(size_categories), 
                        ["small", "medium", "large", "small", "medium", "large"])


class TestMethodInfo(unittest.TestCase):
    """Testes para a classe MethodInfo"""

    def test_15_method_info_creation(self):
        """Teste 15: Verifica criação de MethodInfo"""
        method = MethodInfo(
            name="testMethod",
            file_path="Test.java",
            start_line=10,
            end_line=20,
            size_lines=11,
            repository="test_repo",
            commit_count=5,
            fix_commit_count=2,
            fix_ratio=0.4,
            codeshovel_data={}
        )
        
        self.assertEqual(method.name, "testMethod")
        self.assertEqual(method.size_lines, 11)
        self.assertEqual(method.fix_ratio, 0.4)


class TestIntegration(unittest.TestCase):
    """Testes de integração"""

    def setUp(self):
        """Configuração antes de cada teste"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Limpeza após cada teste"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_16_end_to_end_workflow(self):
        """Teste 16: Verifica fluxo completo de análise (simulado)"""
        # Este teste simula o fluxo completo sem executar o CodeShovel
        
        # 1. Criar estrutura de repositório (sem "test" no nome)
        repo_path = Path(self.temp_dir) / "repos" / "sample_repo"
        repo_path.mkdir(parents=True)
        
        # 2. Criar arquivo JAR falso
        jar_path = Path(self.temp_dir) / "codeshovel.jar"
        with open(jar_path, "w") as f:
            f.write("fake jar")
        
        # 3. Criar arquivo Java com conteúdo
        java_file = repo_path / "Example.java"
        java_content = """
public class Example {
    public void simpleMethod() {
        System.out.println("Hello");
    }
}
"""
        with open(java_file, "w") as f:
            f.write(java_content)
        
        # 4. Inicializar analisador
        analyzer = CodeShovelAnalyzer(str(jar_path), str(repo_path.parent))
        
        # 5. Verificar que tudo foi inicializado corretamente
        self.assertTrue(analyzer.results_dir.exists())
        java_files = analyzer.find_java_files(repo_path)
        self.assertEqual(len(java_files), 1)


def run_tests():
    """Executa todos os testes e retorna resultado"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    unittest.main(verbosity=2)

