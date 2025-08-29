
# Relatório de Análise de Fix vs Tamanho de Métodos

## Resumo Executivo
- **Total de métodos analisados**: 6941
- **Total de repositórios**: 1
- **Métodos com commits de fix**: 2441
- **Tamanho médio dos métodos**: 4.9 linhas
- **Proporção média de fix**: 9.68%

## Análise por Categoria de Tamanho

### Métodos Pequenos (≤10 linhas)
- **Quantidade**: 6337
- **Fix ratio médio**: 9.13%

### Métodos Médios (11-50 linhas)
- **Quantidade**: 601
- **Fix ratio médio**: 15.38%

### Métodos Grandes (>50 linhas)
- **Quantidade**: 3
- **Fix ratio médio**: 12.49%

## Top 10 Métodos com Maior Fix Ratio
- **getDescription** (spring-boot): 83.33% (5 fixes, 46 linhas)
- **analyze** (spring-boot): 80.00% (4 fixes, 6 linhas)
- **match** (spring-boot): 80.00% (4 fixes, 7 linhas)
- **read** (spring-boot): 75.00% (3 fixes, 9 linhas)
- **isIncludedOnClassPath** (spring-boot): 75.00% (3 fixes, 3 linhas)
- **matches** (spring-boot): 75.00% (3 fixes, 20 linhas)
- **stream** (spring-boot): 75.00% (3 fixes, 3 linhas)
- **getPrefixedName** (spring-boot): 75.00% (3 fixes, 3 linhas)
- **extractContextPath** (spring-boot): 66.67% (2 fixes, 15 linhas)
- **isNestedUrl** (spring-boot): 66.67% (2 fixes, 3 linhas)


## Conclusões
Esta análise revela a relação entre o tamanho dos métodos e a frequência de commits de fix.
Os resultados podem ajudar a entender se métodos maiores tendem a ter mais bugs ou se
métodos menores são mais propensos a mudanças.

## Metodologia
- Utilizou-se o CodeShovel para análise de histórico de métodos
- Commits de fix foram identificados por palavras-chave: fix, bug, issue, problem, error
- Métodos foram categorizados por tamanho: pequeno (≤10), médio (11-50), grande (>50)
- Análise focou em repositórios Java de código aberto

---
*Relatório gerado automaticamente pelo CodeShovel Fix Analysis Tool*
