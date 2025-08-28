
# Relatório de Análise de Fix vs Tamanho de Métodos

## Resumo Executivo
- **Total de métodos analisados**: 2036
- **Total de repositórios**: 1
- **Métodos com commits de fix**: 2036
- **Tamanho médio dos métodos**: 8.2 linhas
- **Proporção média de fix**: 100.00%

## Análise por Categoria de Tamanho

### Métodos Pequenos (≤10 linhas)
- **Quantidade**: 1721
- **Fix ratio médio**: 100.00%

### Métodos Médios (11-50 linhas)
- **Quantidade**: 280
- **Fix ratio médio**: 100.00%

### Métodos Grandes (>50 linhas)
- **Quantidade**: 35
- **Fix ratio médio**: 100.00%

## Top 10 Métodos com Maior Fix Ratio
- **toString** (spring-framework): 100.00% (1 fixes, 3 linhas)
- **initialValue** (spring-framework): 100.00% (1 fixes, 3 linhas)
- **store** (spring-framework): 100.00% (1 fixes, 10 linhas)
- **store** (spring-framework): 100.00% (1 fixes, 10 linhas)
- **storeToXML** (spring-framework): 100.00% (1 fixes, 3 linhas)
- **storeToXML** (spring-framework): 100.00% (1 fixes, 3 linhas)
- **keySet** (spring-framework): 100.00% (1 fixes, 5 linhas)
- **compare** (spring-framework): 100.00% (1 fixes, 5 linhas)
- **getDepth** (spring-framework): 100.00% (1 fixes, 11 linhas)
- **isMultiValue** (spring-framework): 100.00% (1 fixes, 3 linhas)


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
