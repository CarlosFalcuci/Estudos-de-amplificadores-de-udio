# Estudos de amplificadores de áudio

Pesquisa de circuitos amplificadores com ênfase na configuração CFP, empregando **LTspice** e **Python/PyLTSpice** para varreduras paramétricas e análise do ganho de tensão, distorção harmônica total (THD), frequência de corte superior e slew rate.

## Organização

- `circuitos/` — esquemático LTspice fornecido.
- `scripts/01_exploracao/` — estudos iniciais e testes da automação.
- `scripts/02_estagio_bjt/` — estudos do estágio com transistores bipolares.
- `scripts/03_cfp_mapeamento/` — varreduras, ganho e distorção do CFP.
- `scripts/04_cfp_frequencia/` — frequência de corte.
- `scripts/05_cfp_slew_rate/` — slew rate.
- `docs/` — metodologia e observações de reprodutibilidade.
- `dados/` e `figuras/` — reservados para resultados.

## Ambiente

Requisitos: Python 3, LTspice instalado no Windows e pacotes de `requirements.txt`.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Atenção:** os scripts foram preservados como recebidos. Contêm caminhos locais absolutos (ajustar `lts`, `asc` e caminhos CSV antes de executar) e alguns dependem de arquivos `.asc` e `.csv` não fornecidos. O esquema disponibilizado `ConfiguracaoCFP_fix.CR.asc` não é automaticamente intercambiável com os demais nomes de netlist. Não foram executadas simulações neste repositório nem validados numericamente os resultados.

Consulte `docs/metodologia.md` para o fluxo de trabalho e `docs/pendencias.md` para as dependências faltantes.

## Origem e status

Material de pesquisa fornecido pelos autores; publicação inicial organizada sem modificações nos cálculos originais. Nenhum resultado de desempenho deve ser interpretado como validado sem execução no ambiente LTspice correspondente.
