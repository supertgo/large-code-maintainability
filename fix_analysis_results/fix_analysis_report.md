
# Relatório de Análise de Fix vs Tamanho de Métodos

## Resumo Executivo
- **Total de métodos analisados**: 15
- **Total de repositórios**: 1
- **Métodos com commits de fix**: 9
- **Tamanho médio dos métodos**: 6.1 linhas
- **Proporção média de fix**: 30.00%

## Análise por Categoria de Tamanho

### Métodos Pequenos (≤10 linhas)
- **Quantidade**: 12
- **Fix ratio médio**: 29.17%

### Métodos Médios (11-50 linhas)
- **Quantidade**: 3
- **Fix ratio médio**: 33.33%

### Métodos Grandes (>50 linhas)
- **Quantidade**: 0
- **Fix ratio médio**: 0.00%

## Top 10 Métodos com Maior Fix Ratio
- **estaVazia** (estruturas-de-dados): 50.00% (1 fixes, 3 linhas)
- **adiciona** (estruturas-de-dados): 50.00% (1 fixes, 6 linhas)
- **adiciona** (estruturas-de-dados): 50.00% (1 fixes, 11 linhas)
- **remover** (estruturas-de-dados): 50.00% (1 fixes, 11 linhas)
- **tamanho** (estruturas-de-dados): 50.00% (1 fixes, 3 linhas)
- **verificaPosi** (estruturas-de-dados): 50.00% (1 fixes, 8 linhas)
- **updateTam** (estruturas-de-dados): 50.00% (1 fixes, 3 linhas)
- **getTamanho** (estruturas-de-dados): 50.00% (1 fixes, 3 linhas)
- **setTamanho** (estruturas-de-dados): 50.00% (1 fixes, 3 linhas)
- **enfileira** (estruturas-de-dados): 0.00% (0 fixes, 5 linhas)


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
