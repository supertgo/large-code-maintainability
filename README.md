# Análise de Commits de Bug/Fix em Métodos Java

## Membros do Grupo

 - Arthur Araujo Rabelo
 - Bruna Saturnino de Carvalho
 - Rafael Araujo Magesty
 - Thiago Roberto Magalhaes

## Explicação do Sistema

Este projeto tem como objetivo analisar a relação entre o tamanho dos métodos Java e a frequência de commits de bug/fix, utilizando técnicas de análise de código e mineração de repositórios. O sistema coleta dados históricos de métodos em repositórios Java de código aberto e identifica padrões que podem indicar se métodos maiores tendem a ter mais bugs ou se métodos menores são mais propensos a mudanças.

### Funcionalidades Principais:
- **Extração de Métodos**: Identifica e extrai métodos Java de repositórios
- **Análise de Histórico**: Utiliza o CodeShovel para rastrear mudanças em métodos ao longo do tempo
- **Classificação de Commits**: Identifica commits de bug/fix baseado em palavras-chave
- **Análise Estatística**: Correlaciona tamanho dos métodos com frequência de bugs
- **Visualização de Dados**: Gera gráficos e relatórios para análise dos resultados

### Metodologia:
1. Clonagem de repositórios Java populares
2. Extração automática de métodos com diferentes tamanhos
3. Análise do histórico de commits de cada método
4. Identificação de commits de fix baseado em mensagens de commit
5. Cálculo de métricas de correlação entre tamanho e frequência de bugs
6. Geração de relatórios e visualizações

## Tecnologias Utilizadas

### Tecnologia Principal
- **CodeShovel**: Biblioteca Java para análise de histórico de código, permitindo rastrear mudanças em métodos específicos ao longo do tempo

### Tecnologias de Desenvolvimento
- **Python 3.x**: Linguagem principal para desenvolvimento do sistema
- **Java**: Necessário para execução do CodeShovel
- **Git**: Controle de versão e clonagem de repositórios

### Bibliotecas Python
- **pandas**: Manipulação e análise de dados
- **matplotlib/seaborn**: Geração de gráficos e visualizações
- **json**: Processamento de dados JSON retornados pelo CodeShovel
- **subprocess**: Execução do CodeShovel via linha de comando
- **pathlib**: Manipulação de caminhos de arquivos
- **argparse**: Interface de linha de comando

### Ferramentas de Análise
- **CodeShovel JAR**: Executável Java para análise de histórico de código
- **Git**: Para clonagem e análise de repositórios

### Tecnologias de Visualização
- **matplotlib**: Gráficos de dispersão e histogramas
- **seaborn**: Visualizações estatísticas avançadas
- **pandas**: Geração de relatórios em formato tabular

### Estrutura de Dados
- **JSON**: Formato de saída do CodeShovel
- **CSV**: Exportação de resultados para análise externa
- **Markdown**: Geração de relatórios em formato legível

### Metodologia de Análise
- **Mineração de Repositórios**: Análise de histórico de commits
- **Análise Estatística**: Correlação entre variáveis
- **Machine Learning**: Possível aplicação de algoritmos de classificação (futuro)
- **Visualização de Dados**: Técnicas de visualização para insights

Este projeto contribui para o entendimento da relação entre complexidade de código e manutenibilidade, fornecendo insights valiosos para desenvolvedores e equipes de desenvolvimento de software.

## Uso

### Instalação de Dependências

Instale as dependências Python necessárias:

```bash
pip install -r requirements.txt
```

### Análise de um Repositório

Execute a análise em um repositório (URL git ou caminho local):

```bash
python3 lcm_cli.py analyze --repo <url-ou-caminho>
```

O sistema executa em modo incremental, salvando o progresso por método. Se a análise for interrompida, você pode executar o mesmo comando novamente para continuar de onde parou.

Exemplos:

```bash
# Com URL git (clona temporariamente)
python3 lcm_cli.py analyze --repo https://github.com/spring-projects/spring-boot.git

# Com repositório local
python3 lcm_cli.py analyze --repo /caminho/para/repo

# Com caminho customizado para codeshovel.jar
python3 lcm_cli.py analyze --repo ./meu-repo --codeshovel-jar /caminho/para/codeshovel.jar

# Especificando diretório de resultados
python3 lcm_cli.py analyze --repo ./meu-repo --results-dir ./resultados

# Mantendo o clone temporário após a análise
python3 lcm_cli.py analyze --repo https://github.com/user/repo.git --keep-clone
```

Argumentos disponíveis:
- `--repo` (obrigatório): URL git ou caminho local do repositório
- `--codeshovel-jar` (opcional): Caminho do codeshovel.jar (padrão: `codeshovel.jar`)
- `--results-dir` (opcional): Diretório para salvar resultados (padrão: diretório atual)
- `--workdir` (opcional): Diretório de trabalho temporário (padrão: `./.lcm_work`)
- `--keep-clone` (opcional): Mantém o clone temporário após a análise

Os resultados são salvos no diretório especificado (ou no diretório atual por padrão) e incluem:
- Arquivos JSON com dados incrementais por método
- Relatório HTML com gráficos e estatísticas
- Relatório Markdown
- Visualizações em PNG

### Análise de Múltiplos Repositórios

Para executar a análise em todos os repositórios dentro de uma pasta (cada subpasta contendo `.git`):

```bash
python3 lcm_cli.py analyze-dir --repos-dir /caminho/para/pasta_dos_repos
```

Exemplos:

```bash
# Análise de todos os repositórios na pasta repos
python3 lcm_cli.py analyze-dir --repos-dir ./repos

# Com diretório de resultados customizado
python3 lcm_cli.py analyze-dir --repos-dir ./repos --results-dir ./resultados
```

Argumentos disponíveis:
- `--repos-dir` (obrigatório): Pasta contendo múltiplos repositórios git
- `--codeshovel-jar` (opcional): Caminho do codeshovel.jar (padrão: `codeshovel.jar`)
- `--results-dir` (opcional): Diretório para salvar resultados (padrão: diretório atual)

Cada repositório terá seus resultados salvos no diretório especificado, além de um relatório e visualizações agregadas.

### Comportamento Incremental

O sistema trabalha de forma incremental por padrão:
- Extrai repositórios, arquivos e métodos uma vez
- Processa métodos individualmente, salvando progresso após cada método
- Se interrompido, o progresso é preservado
- Ao executar novamente, continua de onde parou
- Quando todos os métodos são processados, o arquivo JSON é removido automaticamente
