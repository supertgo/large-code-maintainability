
        # Relatório de Análise de Fix vs Tamanho de Métodos

        ## Resumo Executivo
        - **Total de métodos analisados**: 16
        - **Total de repositórios**: 1
        - **Métodos com commits de fix**: 9
        - **Tamanho médio dos métodos**: 6.3 linhas
        - **Proporção média de fix**: 12.31%

        ## Análise por Categoria de Tamanho

        ### Métodos Pequenos (≤10 linhas)
        - **Quantidade**: 14
        - **Fix ratio médio**: 14.07%

        ### Métodos Médios (11-50 linhas)
        - **Quantidade**: 2
        - **Fix ratio médio**: 0.00%

        ### Métodos Grandes (>50 linhas)
        - **Quantidade**: 0
        - **Fix ratio médio**: 0.00%

        ## Top 10 Métodos com Maior Fix Ratio
        - **onClose** (javalin): 33.33% (4 fixes, 3 linhas)
- **onConnect** (javalin): 33.33% (4 fixes, 3 linhas)
- **onError** (javalin): 33.33% (4 fixes, 3 linhas)
- **onMessage** (javalin): 33.33% (4 fixes, 3 linhas)
- **start** (javalin): 17.65% (15 fixes, 4 linhas)
- **start** (javalin): 16.67% (2 fixes, 4 linhas)
- **onBinaryMessage** (javalin): 16.67% (1 fixes, 3 linhas)
- **port** (javalin): 8.33% (1 fixes, 3 linhas)
- **stop** (javalin): 4.35% (1 fixes, 7 linhas)
- **javalinServlet** (javalin): 0.00% (0 fixes, 3 linhas)

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
        