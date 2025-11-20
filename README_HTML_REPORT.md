# Geração de Relatórios HTML

Este módulo permite gerar relatórios HTML interativos e visualmente atraentes com gráficos e análises dos resultados da análise de métodos.

## Estrutura Modular

O código foi organizado de forma modular:

- **`html_report_generator.py`**: Módulo principal que contém toda a lógica de geração de HTML
- **`fix_analysis.py`**: Importa e usa o `html_report_generator.py`
- **`generate_html_report.py`**: Script standalone para gerar HTML a partir de resultados salvos

## Uso

### 1. Gerar HTML a partir de resultados salvos

Se você já executou uma análise e tem arquivos JSON de resultado:

```bash
python generate_html_report.py --results-dir ./fix_analysis_results_ed
```

Opções:
- `--results-dir`: Diretório contendo os arquivos `*_fix_analysis.json` (padrão: `./fix_analysis_results`)
- `--codeshovel-jar`: Caminho para o JAR do CodeShovel (padrão: `./codeshovel.jar`)

### 2. Gerar HTML durante análise completa

Ao executar uma análise completa, o HTML é gerado automaticamente:

```bash
python large-code-maintainability/lcm_cli.py analyze \
  --repo https://github.com/spring-projects/spring-boot.git \
  --codeshovel-jar large-code-maintainability/codeshovel.jar
```

O relatório HTML será salvo em `fix_analysis_results/fix_analysis_report.html`.

### 3. Usar o módulo programaticamente

Você pode usar o `HTMLReportGenerator` diretamente no seu código:

```python
from html_report_generator import HTMLReportGenerator
import pandas as pd

# Criar dados (exemplo)
df = pd.DataFrame({
    'method_name': ['methodA', 'methodB'],
    'repository': ['repo1', 'repo1'],
    'size_lines': [10, 25],
    'commit_count': [5, 8],
    'fix_commit_count': [1, 3],
    'fix_ratio': [0.2, 0.375]
})

# Gerar HTML
generator = HTMLReportGenerator(output_dir="meus_resultados")
html_file = generator.generate_html(df)
print(f"HTML gerado em: {html_file}")
```

## Características do Relatório HTML

O relatório HTML gerado inclui:

- **Resumo Executivo**: Cards com estatísticas principais
  - Total de métodos analisados
  - Número de repositórios
  - Métodos com fixes
  - Tamanho médio dos métodos
  - Fix ratio médio

- **Visualizações Gráficas**:
  - Scatter plot: Tamanho vs Fix Ratio
  - Boxplot: Fix Ratio por categoria de tamanho
  - Histograma: Distribuição de tamanhos de métodos
  - Gráfico de barras: Fix Ratio médio por repositório

- **Análise por Categoria**:
  - Métodos pequenos (≤10 linhas)
  - Métodos médios (11-50 linhas)
  - Métodos grandes (>50 linhas)

- **Top 10 Métodos**: Lista dos métodos com maior fix ratio

- **Conclusões e Metodologia**: Explicação dos resultados e métodos usados

## Design Responsivo

O HTML gerado é totalmente responsivo e funciona bem em:
- Desktops
- Tablets
- Smartphones

## Personalização

Para personalizar o relatório, edite o arquivo `html_report_generator.py`:

- **Cores**: Altere as cores no CSS (seção `<style>`)
- **Gráficos**: Modifique o método `create_charts()` para adicionar/remover gráficos
- **Estatísticas**: Ajuste o método `generate_statistics()` para incluir novas métricas
- **Layout**: Edite o método `_build_html_template()` para modificar a estrutura

## Exemplos de Personalização

### Adicionar um novo gráfico

```python
# Em html_report_generator.py, no método create_charts()

# Gráfico 5: Novo gráfico
fig, ax = plt.subplots(figsize=(10, 6))
# ... seu código do gráfico aqui ...
buf = BytesIO()
plt.tight_layout()
plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
buf.seek(0)
charts.append(base64.b64encode(buf.read()).decode("utf-8"))
plt.close()
```

### Alterar o esquema de cores

Procure por essas cores no CSS e altere:
- `#667eea` - Azul primário
- `#764ba2` - Roxo secundário
- `#2E86AB` - Azul dos gráficos
- `#A23B72` - Rosa dos gráficos
- `#F18F01` - Laranja dos gráficos

## Requisitos

- Python 3.7+
- pandas
- matplotlib
- pathlib (incluído no Python 3.4+)

Instale as dependências:

```bash
pip install pandas matplotlib
```

## Troubleshooting

### Erro: "Nenhum resultado encontrado"

Certifique-se de que o diretório especificado contém arquivos `*_fix_analysis.json`.

```bash
ls fix_analysis_results_ed/*_fix_analysis.json
```

### Erro: "DataFrame vazio"

Os arquivos JSON podem estar no formato incorreto. Verifique se contêm dados válidos:

```bash
head -n 20 fix_analysis_results_ed/spring-boot_fix_analysis.json
```

### HTML não abre corretamente

Abra o arquivo HTML diretamente no navegador:

```bash
# Linux
xdg-open fix_analysis_results/fix_analysis_report.html

# MacOS
open fix_analysis_results/fix_analysis_report.html

# Windows
start fix_analysis_results/fix_analysis_report.html
```

## Contribuindo

Para adicionar novas funcionalidades ao módulo HTML:

1. Edite `html_report_generator.py`
2. Mantenha a modularidade - crie métodos separados para cada funcionalidade
3. Documente suas alterações
4. Teste com diferentes conjuntos de dados

## Licença

Veja o arquivo LICENSE no diretório raiz do projeto.

