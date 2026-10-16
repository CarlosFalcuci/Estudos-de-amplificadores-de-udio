from PyLTSpice import SimRunner, SpiceEditor, LTSpiceLogReader
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# CAMINHOS
# ============================================================

lts = r"C:\Users\Carlos Eduardo\AppData\Local\Programs\ADI\LTspice\LTspice.exe"
asc = r"C:\Users\Carlos Eduardo\Documents\LTspice\ConfiguracaoCFP_fix.asc"

csv_saida = r"C:\Users\Carlos Eduardo\Documents\Workspace_VSCODE\Pesquisa\thd_vs_av_correntes_jfet.csv"
fig_saida = r"C:\Users\Carlos Eduardo\Documents\Workspace_VSCODE\Pesquisa\thd_vs_av_correntes_jfet.png"

runner = SimRunner(
    output_folder="./teste_py_lt",
    simulator=lts
)

# ============================================================
# CONFIGURAÇÕES DA VARREDURA
# ============================================================

correntes_mA = [
    1.0,
    10.0
]

percentuais_jfet = [
    0.01,
    0.05,
    0.1,
    0.15,
    0.2
]

Av_inicio = 7
Av_fim = 17

n_pontos = 50
folga = 0.10

resultados = []

# ============================================================
# LOOP PRINCIPAL
# ============================================================

plt.figure(figsize=(10, 6))

for I_mA in correntes_mA:

    I = I_mA * 1e-3

    # Corrente por ramo, seguindo a lógica original:
    # Rd = 20 / (I/2)
    I_ramo = I / 2

    Rd = 20 / I_ramo

    Rs_Av7 = Rd / (2 * Av_inicio)
    Rs_Av17 = Rd / (2 * Av_fim)

    Rs_max = Rs_Av7 * (1 + folga)
    Rs_min = Rs_Av17 * (1 - folga)

    Rs_values = np.linspace(Rs_max, Rs_min, n_pontos)

    for percentual in percentuais_jfet:

        # Corrente no JFET
        # Exemplo: percentual = 0.20 significa 20% da corrente do ramo
        I_jfet = percentual * I_ramo

        # Relação corrigida:
        # I_JFET = 0.62/R13 = 0.62/R14
        R_jfet = 0.62 / I_jfet

        x_av = []
        y_thd = []

        print("\n====================================")
        print(f"I total = {I_mA:.3f} mA")
        print(f"I por ramo = {I_ramo*1e3:.3f} mA")
        print(f"Percentual no JFET = {percentual*100:.0f} %")
        print(f"I_JFET = {I_jfet*1e3:.3f} mA")
        print(f"R13 = R14 = {R_jfet:.3f} ohm")
        print(f"Rd = {Rd:.3f} ohm")
        print(f"Rs aproximado para Av=7  -> {Rs_Av7:.3f} ohm")
        print(f"Rs aproximado para Av=17 -> {Rs_Av17:.3f} ohm")
        print(f"Varredura Rs: {Rs_max:.3f} até {Rs_min:.3f} ohm")
        print("====================================")

        for Rs in Rs_values:

            net = SpiceEditor(asc)

            # Fonte de corrente principal
            net.set_component_value("I1", f"{I:.12g}")

            # Resistores de dreno
            net.set_component_value("Rd1e", f"{Rd:.12g}")
            net.set_component_value("Rd1d", f"{Rd:.12g}")

            # Resistores de fonte, usados para varrer o ganho
            net.set_component_value("Rs1e", f"{Rs:.12g}")
            net.set_component_value("Rs1d", f"{Rs:.12g}")

            # Resistores que definem a corrente dos JFETs
            net.set_component_value("R13", f"{R_jfet:.12g}")
            net.set_component_value("R14", f"{R_jfet:.12g}")

            try:
                raw, log_path = runner.run_now(net)
                log = LTSpiceLogReader(log_path)

                thd = log.fourier["V(vout)"][0].thd

                vpp = float(log.dataset["vpp"][0])

                # Pelo seu critério:
                # Av = Vpp/2
                av = vpp / 2

                x_av.append(av)
                y_thd.append(thd)

                resultados.append({
                    "I_total_mA": I_mA,
                    "I_total_A": I,
                    "I_ramo_mA": I_ramo * 1e3,
                    "percentual_jfet": percentual,
                    "percentual_jfet_percent": percentual * 100,
                    "I_jfet_mA": I_jfet * 1e3,
                    "R13_ohm": R_jfet,
                    "R14_ohm": R_jfet,
                    "Rd_ohm": Rd,
                    "Rs_ohm": Rs,
                    "Av_aproximado_teorico": Rd / (2 * Rs),
                    "Av_medido_Vpp_sobre_2": av,
                    "THD_percent": thd
                })

                print(
                    f"I = {I_mA:6.3f} mA | "
                    f"JFET = {percentual*100:5.1f} % | "
                    f"R13=R14 = {R_jfet:10.3f} ohm | "
                    f"Rs = {Rs:10.3f} ohm | "
                    f"Av_teor = {Rd/(2*Rs):8.3f} | "
                    f"Av_med = {av:8.3f} | "
                    f"THD = {thd:8.5f} %"
                )

            except Exception as e:
                print(
                    f"ERRO | "
                    f"I = {I_mA:.3f} mA | "
                    f"JFET = {percentual*100:.1f} % | "
                    f"Rs = {Rs:.3f} ohm | "
                    f"R13=R14 = {R_jfet:.3f} ohm -> {e}"
                )

        # Só plota se tiver pontos válidos
        if len(x_av) > 0:

            dados_curva = pd.DataFrame({
                "Av": x_av,
                "THD": y_thd
            }).sort_values("Av")

            plt.plot(
                dados_curva["Av"],
                dados_curva["THD"],
                marker="o",
                linestyle="-",
                label=f"I = {I_mA:g} mA | JFET = {percentual*100:.0f}%"
            )

# ============================================================
# SALVAR CSV
# ============================================================

df_saida = pd.DataFrame(resultados)

df_saida.to_csv(
    csv_saida,
    index=False,
    encoding="utf-8-sig"
)

print(f"\nCSV salvo em: {csv_saida}")

# ============================================================
# PLOT FINAL
# ============================================================

plt.title("THD vs AV para diferentes correntes e correntes nos JFETs")
plt.xlabel("AV = Vpp/2")
plt.ylabel("THD (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig(fig_saida, dpi=600, bbox_inches="tight")
plt.show()

print(f"Figura salva em: {fig_saida}")