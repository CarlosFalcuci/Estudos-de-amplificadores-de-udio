# Fluxo de trabalho da pesquisa

1. Definir o circuito no LTspice e suas condições de polarização.
2. Escolher correntes, resistores e ganhos-alvo.
3. Usar Python/PyLTSpice para alterar os componentes e executar as análises disponíveis.
4. Ler os arquivos RAW e LOG; extrair ganho, THD, frequência de corte superior e slew rate de acordo com cada script.
5. Registrar as varreduras, gerar gráficos e comparar pontos de operação.

## Interpretação dos scripts

- `mapeamentodeganho`: varredura de correntes e valores de Rs; seleciona o ponto com menor erro absoluto em relação a um ganho-alvo e registra THD, quando disponível.
- `EstudodecorrenteCFP`: relaciona corrente de ramo e fração destinada aos JFETs, modificando R13/R14; analisa THD x ganho.
- `FC_at1`: utiliza resultados previamente exportados para estudar frequência de corte x corrente.
- `Slew_rate(1)` e `SlewRate_CFP_1E`: extraem medidas temporais do log da simulação para estimar slew rate.
- `1E` e `1E_THD`: estudos de frequência e distorção do estágio identificado como BJT nos nomes dos arquivos.

A execução depende do LTspice e dos esquemáticos originais; **não** foi validada automaticamente neste ambiente.
