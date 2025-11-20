# Análise de Commits de Bug/Fix em Métodos Java

## Membros do Grupo

- Arthur Araujo Rabelo
- Bruna Saturnino de Carvalho
- Rafael Araujo Magesty
- Thiago Roberto Magalhaes

## Objetivo da Ferramenta

Esta ferramenta analisa a relação entre o tamanho dos métodos Java e a frequência de commits de bug/fix em repositórios de código aberto. O sistema coleta dados históricos de métodos, rastreia mudanças ao longo do tempo e identifica padrões que podem indicar se métodos maiores tendem a ter mais bugs ou se métodos menores são mais propensos a mudanças.

A ferramenta extrai métodos de repositórios Java, analisa seu histórico de commits usando o CodeShovel, identifica commits de fix baseado em palavras-chave e gera relatórios estatísticos e visualizações para análise dos resultados.

## Tecnologias Utilizadas

**Linguagens e Ferramentas:**
- Python 3.7+
- Java 8+ (para execução do CodeShovel)
- Git (para clonagem de repositórios)

**Bibliotecas Python:**
- pandas: manipulação e análise de dados
- matplotlib/seaborn: geração de gráficos e visualizações
- numpy: operações numéricas
- pytest: framework de testes

**Ferramentas de Análise:**
- CodeShovel: biblioteca Java para análise de histórico de código e rastreamento de mudanças em métodos específicos

**Formatos de Saída:**
- JSON: armazenamento de dados incrementais
- HTML: relatórios interativos
- Markdown: relatórios em texto
- PNG: visualizações gráficas

## Como Instalar a Ferramenta

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd large-code-maintainability
```

2. Instale as dependências Python:
```bash
pip install -r requirements.txt
```

3. Instale as dependências de teste (opcional):
```bash
pip install -r requirements-test.txt
```

4. Certifique-se de que o arquivo `codeshovel.jar` está presente no diretório raiz do projeto. Se necessário, baixe ou compile o CodeShovel e coloque o arquivo JAR no diretório do projeto.

5. Verifique se você tem Java 8 ou superior instalado:
```bash
java -version
```

## Como Utilizar a Ferramenta

### Análise de um Repositório

Para analisar um único repositório (URL git ou caminho local):

```bash
python3 lcm_cli.py analyze --repo <url-ou-caminho>
```

Exemplos:

```bash
# Com URL git (clona temporariamente)
python3 lcm_cli.py analyze --repo https://github.com/spring-projects/spring-boot.git

# Com repositório local
python3 lcm_cli.py analyze --repo /caminho/para/repo

# Com caminho customizado para codeshovel.jar
python3 lcm_cli.py analyze --repo ./meu-repo --codeshovel-jar /caminho/para/codeshovel.jar

# Com modo incremental
python3 lcm_cli.py analyze --repo ./meu-repo --codeshovel-jar codeshovel.jar --incremental

# Com modo incremental e diretório de resultados customizado
python3 lcm_cli.py analyze --repo ./meu-repo --codeshovel-jar codeshovel.jar --incremental --results-dir ./resultados

# Mantendo o clone temporário após a análise
python3 lcm_cli.py analyze --repo https://github.com/user/repo.git --codeshovel-jar codeshovel.jar --keep-clone
```

**Argumentos disponíveis:**
- `--repo` (obrigatório): URL git ou caminho local do repositório
- `--codeshovel-jar` (obrigatório): Caminho do codeshovel.jar
- `--workdir` (opcional): Diretório de trabalho temporário (padrão: `./.lcm_work`)
- `--keep-clone` (opcional): Mantém o clone temporário após a análise
- `--incremental` (opcional): Executa em modo incremental, salvando progresso por método
- `--results-dir` (opcional): Pasta para salvar resultados incrementais (padrão: `./fix_analysis_results`)

Quando o modo incremental não é usado, os resultados são salvos no diretório padrão ou especificado. No modo incremental, os resultados são salvos no diretório especificado com `--results-dir`. Os resultados incluem:
- Arquivo JSON com dados incrementais por método
- Relatório HTML com gráficos e estatísticas
- Relatório Markdown
- Visualizações em PNG

### Análise de Múltiplos Repositórios

Para executar a análise em todos os repositórios dentro de uma pasta:

```bash
python3 lcm_cli.py analyze-dir --repos-dir /caminho/para/pasta_dos_repos
```

Exemplos:

```bash
# Análise de todos os repositórios na pasta repos
python3 lcm_cli.py analyze-dir --repos-dir ./repos

# Com modo incremental
python3 lcm_cli.py analyze-dir --repos-dir ./repos --codeshovel-jar codeshovel.jar --incremental

# Com diretório de resultados customizado
python3 lcm_cli.py analyze-dir --repos-dir ./repos --codeshovel-jar codeshovel.jar --results-dir ./resultados

# Com modo incremental e diretório de resultados customizado
python3 lcm_cli.py analyze-dir --repos-dir ./repos --codeshovel-jar codeshovel.jar --incremental --results-dir ./resultados
```

**Argumentos disponíveis:**
- `--repos-dir` (obrigatório): Pasta contendo múltiplos repositórios git (subpastas com .git)
- `--codeshovel-jar` (obrigatório): Caminho do codeshovel.jar
- `--incremental` (opcional): Executa em modo incremental, salvando progresso por método
- `--results-dir` (opcional): Diretório para salvar resultados (padrão: `./fix_analysis_results`)

### Modo Incremental

O argumento `--incremental` permite executar a análise em modo incremental:

```bash
# Com modo incremental
python3 lcm_cli.py analyze --repo ./meu-repo --codeshovel-jar codeshovel.jar --incremental

# Com modo incremental e diretório de resultados customizado
python3 lcm_cli.py analyze --repo ./meu-repo --codeshovel-jar codeshovel.jar --incremental --results-dir ./resultados
```

No modo incremental:
- Extrai repositórios, arquivos e métodos uma vez e salva em arquivo JSON
- Processa métodos individualmente, salvando progresso após cada método
- Se interrompida, o progresso é preservado no arquivo JSON
- Ao executar novamente, continua de onde parou sem reprocessar métodos já analisados
- Os resultados são salvos no diretório especificado com `--results-dir`

Sem o modo incremental, a ferramenta processa todos os métodos em memória e gera os relatórios diretamente.

## Como Executar os Testes Localmente

Para executar os testes unitários:

```bash
pytest
```

Para executar os testes com relatório de cobertura:

```bash
pytest --cov=. --cov-report=html
```

Para executar testes específicos:

```bash
pytest test_fix_analysis.py
```

Para executar com mais verbosidade:

```bash
pytest -v
```

Os testes estão configurados no arquivo `pytest.ini` e cobrem as principais funcionalidades da ferramenta, incluindo extração de métodos, análise de commits e geração de relatórios.
