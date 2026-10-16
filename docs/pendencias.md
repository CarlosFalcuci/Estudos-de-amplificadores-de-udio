# Dependências e verificações pendentes

## Esquemáticos mencionados e não disponibilizados com os scripts

- `pestagio.asc`
- `pestagio1.asc`
- `1_estagio_tbj.asc`
- `1E.asc`
- `1E_thd.asc`
- `ConfiguracaoCFP.asc`
- `ConfiguracaoCFP_FC_fix.asc`
- `ConfiguracaoCFP_SR_fix.asc`
- `teste_py.asc`

O usuário disponibilizou o esquema **`ConfiguracaoCFP_fix.CR.asc`** separadamente. Não presumir equivalência entre esquemáticos diferentes. Até o upload do respectivo arquivo para `circuitos/`, ele deve ser incluído manualmente.

## Antes de executar

1. Substituir caminhos absolutos `C:\Users\...` por caminhos locais.
2. Fornecer os CSVs intermediários esperados em alguns scripts.
3. Confirmar a amplitude de entrada antes de interpretar `Av = Vpp / 2` como ganho.
4. Revisar `Is_sobre_2_mA` em `Slew_rate(1).py` (divisão/multiplicação divergentes).
5. Revisar percentual JFET em `SlewRate_CFP_1E.py` versus arquivo `jfet20`.
6. Conferir a configuração de comandos LTspice, nomes de nós e faixas de varredura.
7. Comparar curvas e simulações em condições equivalentes antes de tirar conclusões científicas.
