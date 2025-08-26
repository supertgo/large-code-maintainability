# 🔍 CodeShovel Fix Analysis Tool

Esta ferramenta automatiza a análise da relação entre o tamanho dos métodos Java e a frequência de commits de "fix" usando o CodeShovel. Ela permite investigar se métodos maiores tendem a ter mais bugs ou se métodos menores são mais propensos a mudanças.

## 🎯 Objetivo

Analisar automaticamente a correlação entre:
- **Tamanho dos métodos** (número de linhas)
- **Frequência de commits de fix** (commits com palavras-chave como "fix", "bug", "issue", etc.)
- **Histórico de mudanças** dos métodos ao longo do tempo

## 🚀 Funcionalidades

- ✅ **Análise automática** de repositórios Java usando CodeShovel
- ✅ **Detecção inteligente** de commits de fix por palavras-chave
- ✅ **Categorização por tamanho** (pequeno ≤10, médio 11-50, grande >50 linhas)
- ✅ **Estatísticas detalhadas** e correlações
- ✅ **Visualizações gráficas** (scatter plots, box plots, histogramas)
- ✅ **Relatórios em Markdown** com insights
- ✅ **Exportação de dados** em CSV e Excel
- ✅ **Análise por repositório** ou múltiplos repositórios

## 📋 Pré-requisitos

### Software
- **Python 3.7+**
- **Java 8+** (para executar o CodeShovel)
- **Git** (para clonar repositórios)

### Dependências Python
```bash
pip install -r requirements.txt
```

### CodeShovel
- Baixe o JAR do CodeShovel ou compile o projeto
- Certifique-se de que o arquivo `codeshovel.jar` está acessível

## 🛠️ Instalação

1. **Clone este repositório:**
```bash
git clone <seu-repositorio>
cd codeshovel-fix-analysis
```

2. **Instale as dependências Python:**
```bash
pip install -r requirements.txt
```

3. **Prepare os repositórios Java:**
```bash
# Clone repositórios de exemplo
bash bin/clone-java-repositories.sh ./repos

# Ou clone seus próprios repositórios Java
git clone https://github.com/seu-repo/java-project.git ./repos/
```

## 📖 Como Usar

### Uso Básico

```bash
python run_analysis.py --codeshovel-jar codeshovel.jar --repositories-dir ./repos
```

### Uso Avançado

```bash
python run_analysis.py \
  --codeshovel-jar codeshovel.jar \
  --repositories-dir ./repos \
  --repo-limit 10 \
  --method-limit 100
```

### Parâmetros

- `--codeshovel-jar`: Caminho para o JAR do CodeShovel
- `--repositories-dir`: Diretório contendo os repositórios Java
- `--repo-limit`: Limite de repositórios para analisar (padrão: 5)
- `--method-limit`: Limite de métodos por repositório (padrão: 50)

## 🔧 Exemplos de Uso

### 1. Análise de Repositório Único

```python
from fix_analysis import CodeShovelAnalyzer

# Inicializar analisador
analyzer = CodeShovelAnalyzer("codeshovel.jar", "./repos")

# Analisar repositório específico
analyses = analyzer.analyze_repository("checkstyle")

# Gerar estatísticas
stats = analyzer.generate_statistics(analyses)
print(f"Fix ratio médio: {stats['avg_fix_ratio']:.2%}")
```

### 2. Análise Personalizada

```python
# Analisar múltiplos repositórios
repos = ["checkstyle", "commons-lang", "junit4"]
all_analyses = []

for repo in repos:
    analyses = analyzer.analyze_repository(repo)
    all_analyses.extend(analyses)

# Criar visualizações
analyzer.create_visualizations(all_analyses)

# Gerar relatório
analyzer.generate_report(all_analyses)
```

### 3. Exportação de Dados

```python
# Converter para DataFrame
import pandas as pd

data = []
for analysis in analyses:
    data.append({
        'method_name': analysis.method_info.name,
        'size_lines': analysis.method_info.size_lines,
        'fix_ratio': analysis.method_info.fix_ratio
    })

df = pd.DataFrame(data)

# Salvar como CSV
df.to_csv("fix_analysis.csv", index=False)

# Calcular correlação
correlation = df['size_lines'].corr(df['fix_ratio'])
print(f"Correlação: {correlation:.3f}")
```

## 📊 Saídas da Ferramenta

### 1. Arquivos JSON
- `{repo_name}_fix_analysis.json`: Resultados detalhados por repositório

### 2. Visualizações
- `fix_analysis_visualization.png`: Gráficos de correlação e distribuição

### 3. Relatórios
- `fix_analysis_report.md`: Relatório completo em Markdown

### 4. Dados Exportados
- `fix_analysis_data.csv`: Dados em formato CSV
- `fix_analysis_data.xlsx`: Dados em formato Excel (se openpyxl estiver instalado)

## 📈 Interpretação dos Resultados

### Métricas Principais

1. **Fix Ratio**: Proporção de commits de fix em relação ao total de commits
2. **Correlação**: Relação estatística entre tamanho do método e fix ratio
3. **Categorias de Tamanho**:
   - **Pequeno** (≤10 linhas): Métodos simples, geralmente menos propensos a bugs
   - **Médio** (11-50 linhas): Métodos moderados, equilíbrio entre complexidade e manutenibilidade
   - **Grande** (>50 linhas): Métodos complexos, potencialmente mais propensos a bugs

### Insights Esperados

- **Métodos pequenos**: Geralmente têm menor fix ratio
- **Métodos médios**: Fix ratio moderado, bom equilíbrio
- **Métodos grandes**: Podem ter maior fix ratio devido à complexidade

## 🔍 Detecção de Commits de Fix

A ferramenta identifica commits de fix usando palavras-chave:

- **fix**: Correções gerais
- **bug**: Correções de bugs
- **issue**: Resolução de problemas
- **problem**: Solução de problemas
- **error**: Correções de erros

## ⚠️ Limitações e Considerações

1. **Performance**: Análise de repositórios grandes pode ser lenta
2. **Precisão**: Detecção de commits de fix baseada em palavras-chave
3. **Escopo**: Foca em métodos Java (pode ser estendido para outras linguagens)
4. **Memória**: Análise de muitos métodos pode consumir memória significativa

## 🚀 Otimizações

### Para Repositórios Grandes

```bash
# Limitar análise
python run_analysis.py \
  --codeshovel-jar codeshovel.jar \
  --repositories-dir ./repos \
  --repo-limit 3 \
  --method-limit 25
```

### Para Análise Rápida

```bash
# Analisar apenas repositórios pequenos
python run_analysis.py \
  --codeshovel-jar codeshovel.jar \
  --repositories-dir ./repos \
  --repo-limit 2 \
  --method-limit 10
```

## 🐛 Solução de Problemas

### Erro: "CodeShovel JAR não encontrado"
```bash
# Verifique se o arquivo existe
ls -la codeshovel.jar

# Ajuste o caminho no comando
python run_analysis.py --codeshovel-jar /caminho/completo/codeshovel.jar --repositories-dir ./repos
```

### Erro: "Nenhum repositório Git encontrado"
```bash
# Clone repositórios primeiro
bash bin/clone-java-repositories.sh ./repos

# Ou clone manualmente
git clone https://github.com/checkstyle/checkstyle.git ./repos/checkstyle
```

### Erro: "Dependência faltando"
```bash
# Instale as dependências
pip install -r requirements.txt

# Ou instale individualmente
pip install pandas matplotlib seaborn numpy
```

## 📚 Recursos Adicionais

- **Documentação CodeShovel**: [README.md](../README.md)
- **Exemplos de Uso**: [example_usage.py](example_usage.py)
- **Análise Avançada**: [fix_analysis.py](fix_analysis.py)

## 🤝 Contribuição

Para contribuir com melhorias:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Adicione testes se aplicável
5. Envie um pull request

## 📄 Licença

Este projeto está sob a mesma licença do CodeShovel original.

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique a documentação
2. Execute os exemplos
3. Abra uma issue no repositório
4. Consulte os logs de execução

---

**Desenvolvido com ❤️ para análise de qualidade de código** 