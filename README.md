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
- **Execução Incremental**: Salva progresso automaticamente, permitindo retomar análises interrompidas
- **Salvamento Atômico**: Previne corrupção de dados mesmo em caso de interrupção
- **Suporte a URLs Git**: Clona e analisa repositórios diretamente de URLs Git
- **Processamento em Lote**: Analisa múltiplos repositórios em uma única execução

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

## Uso em uma linha (CLI)

### Configuração Inicial

Antes de usar, configure a variável de ambiente `CODESHOVEL_JAR` com o caminho para o arquivo `codeshovel.jar`:

```bash
export CODESHOVEL_JAR=/caminho/para/codeshovel.jar
```

Ou coloque o arquivo `codeshovel.jar` no diretório atual.

### Análise de Repositório Único

Execute a análise em um repositório (URL git ou caminho local) com:

```bash
python run_code_shovel.py --repo <url-ou-caminho> --results-dir <diretorio-resultados>
```

**Parâmetros obrigatórios:**
- `--repo`: Caminho local do repositório ou URL Git (https://, http://, git@, ou termina com .git)
- `--results-dir`: Diretório onde os resultados temporários serão salvos (obrigatório)

**Parâmetros opcionais:**
- `--generate-reports`: Gera visualizações e relatórios após a análise usando `fix_analysis.py`

**Exemplos:**

```bash
# Analisar repositório local
python run_code_shovel.py --repo ./repos/spring-boot --results-dir ./my_results

# Analisar repositório a partir de URL Git (clona automaticamente para ./.lcm_work)
python run_code_shovel.py --repo https://github.com/spring-projects/spring-boot.git --results-dir ./my_results

# Analisar e gerar relatórios/visualizações
python run_code_shovel.py --repo ./repos/spring-boot --results-dir ./my_results --generate-reports

# Analisar repositório SSH
python run_code_shovel.py --repo git@github.com:spring-projects/spring-boot.git --results-dir ./my_results
```

**Notas importantes:**
- Repositórios clonados de URLs são salvos em `./.lcm_work` e mantidos por padrão (não são deletados)
- A execução é **incremental por padrão**: se interrompida, pode ser retomada executando o mesmo comando novamente
- O progresso é salvo **atomicamente** após cada método processado, evitando corrupção de dados em caso de interrupção
- Quando todos os métodos são processados, o arquivo de resultados temporário é automaticamente deletado

### Analisar Múltiplos Repositórios

Para executar a análise em todos os repositórios dentro de uma pasta (cada subpasta contendo `.git`):

```bash
python run_code_shovel.py --repos-dir ./repos --results-dir ./my_results
```

Cada repositório será processado sequencialmente, e os resultados serão salvos no diretório especificado.

### Recuperação após Interrupção

Se a análise for interrompida (Ctrl+C), o progresso é salvo automaticamente. Para retomar:

```bash
# Execute o mesmo comando novamente
python run_code_shovel.py --repo ./repos/spring-boot --results-dir ./my_results
```

O script detectará automaticamente os métodos já processados e continuará de onde parou.

### Geração de Relatórios

Para gerar visualizações e relatórios após a análise:

```bash
python run_code_shovel.py --repo ./repos/spring-boot --results-dir ./my_results --generate-reports
```

Isso gerará:
- Gráficos de correlação e distribuição
- Relatório em Markdown
- Dados exportados em CSV/Excel (se disponível)
