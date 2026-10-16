from PyLTSpice import SimRunner, SpiceEditor, LTSpiceLogReader
import numpy as np
import csv

# ============================================================
# CAMINHOS
# ============================================================

lts = r"C:\Users\Carlos Eduardo\AppData\Local\Programs\ADI\LTspice\LTspice.exe"
runner = SimRunner(output_folder="./teste_py_lt", simulator=lts)

asc = r"C:\Users\Carlos Eduardo\Documents\LTspice\ConfiguracaoCFP.asc"

# ============================================================
# CONFIGURAÇÕES
# ============================================================

correntes = np.linspace(0.0001, 0.01, 30)   # 0.1 mA até 10 mA
ganhos_alvo = [6, 9, 12, 18]
n_pontos_rs = 30

percentual_jfet = 0.20

arquivo_csv = "melhores_ganhos_por_corrente_configuracaoCFP_jfet20.csv"

net_editor = SpiceEditor(asc)

resultados_finais = []

# ============================================================
# VARREDURA PRINCIPAL
# ============================================================

for I1 in correntes:

    # Fonte de corrente principal
    net_editor.set_component_value("I1", f"{I1:.12g}")

    # Corrente por ramo
    I_ramo = I1 / 2

    # 20% da corrente do ramo passa pelo JFET
    I_jfet = percentual_jfet * I_ramo

    # Relação:
    # I_JFET = 0.62/R13 = 0.62/R14
    R_jfet = 0.62 / I_jfet

    net_editor.set_component_value("R13", f"{R_jfet:.12g}")
    net_editor.set_component_value("R14", f"{R_jfet:.12g}")

    # Resistores de dreno
    Rd = 20 / I_ramo

    net_editor.set_component_value("Rd1e", f"{Rd:.12g}")
    net_editor.set_component_value("Rd1d", f"{Rd:.12g}")

    for alvo in ganhos_alvo:

        Rs_central = Rd / (2 * alvo)
        Rs_min = 0.5 * Rs_central
        Rs_max = 1.5 * Rs_central

        resistores = np.linspace(Rs_min, Rs_max, n_pontos_rs)

        melhor = {
            "ganho_alvo": alvo,
            "I1_A": I1,
            "I1_mA": I1 * 1000,
            "I_ramo_mA": I_ramo * 1000,
            "percentual_jfet": percentual_jfet,
            "percentual_jfet_percent": percentual_jfet * 100,
            "I_jfet_mA": I_jfet * 1000,
            "R13_ohm": R_jfet,
            "R14_ohm": R_jfet,
            "Rs_ohm": None,
            "Rd_ohm": Rd,
            "Av_obtido": None,
            "erro": np.inf,
            "THD": None
        }

        for Rs in resistores:

            net_editor.set_component_value("Rs1e", f"{Rs:.12g}")
            net_editor.set_component_value("Rs1d", f"{Rs:.12g}")

            try:
                raw, log_path = runner.run_now(net_editor)
                log = LTSpiceLogReader(log_path)

                vpp = float(log.dataset["vpp"][0])
                av = vpp / 2

                try:
                    thd = log.fourier["V(vout)"][0].thd
                except:
                    thd = None

                erro = abs(av - alvo)

                if erro < melhor["erro"]:
                    melhor["Rs_ohm"] = Rs
                    melhor["Av_obtido"] = av
                    melhor["erro"] = erro
                    melhor["THD"] = thd

            except Exception as e:
                print(
                    f"Erro em I1={I1:.6f} A, "
                    f"alvo={alvo}, "
                    f"Rs={Rs:.2f} ohm, "
                    f"R13=R14={R_jfet:.2f} ohm -> {e}"
                )

        resultados_finais.append(melhor)

# ============================================================
# IMPRESSÃO NO TERMINAL
# ============================================================

print("\n===== RESULTADOS =====\n")

for r in resultados_finais:

    if r["Rs_ohm"] is None:
        print(
            f"Alvo={r['ganho_alvo']:>4} | "
            f"I1={r['I1_mA']:8.4f} mA | "
            f"SEM RESULTADO VÁLIDO"
        )
    else:
        print(
            f"Alvo={r['ganho_alvo']:>4} | "
            f"I1={r['I1_mA']:8.4f} mA | "
            f"I_JFET={r['I_jfet_mA']:8.4f} mA | "
            f"R13=R14={r['R13_ohm']:10.4f} ohm | "
            f"Rs={r['Rs_ohm']:10.4f} ohm | "
            f"Rd={r['Rd_ohm']:10.4f} ohm | "
            f"Av={r['Av_obtido']:10.4f} | "
            f"Erro={r['erro']:10.4f} | "
            f"THD={r['THD']}"
        )

# ============================================================
# SALVAR CSV
# ============================================================

with open(arquivo_csv, mode="w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow([
        "ganho_alvo",
        "I1_A",
        "I1_mA",
        "I_ramo_mA",
        "percentual_jfet",
        "percentual_jfet_percent",
        "I_jfet_mA",
        "R13_ohm",
        "R14_ohm",
        "Rs_ohm",
        "Rd_ohm",
        "Av_obtido",
        "erro",
        "THD"
    ])

    for r in resultados_finais:
        writer.writerow([
            r["ganho_alvo"],
            r["I1_A"],
            r["I1_mA"],
            r["I_ramo_mA"],
            r["percentual_jfet"],
            r["percentual_jfet_percent"],
            r["I_jfet_mA"],
            r["R13_ohm"],
            r["R14_ohm"],
            r["Rs_ohm"],
            r["Rd_ohm"],
            r["Av_obtido"],
            r["erro"],
            r["THD"]
        ])

print(f"\nArquivo CSV salvo com sucesso: {arquivo_csv}")