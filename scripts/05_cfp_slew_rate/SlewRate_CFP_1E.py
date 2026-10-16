from PyLTSpice import SimRunner, SpiceEditor
import pandas as pd
import matplotlib.pyplot as plt
import re

# ============================================================
# CAMINHOS
# ============================================================

lts = r"C:\Users\Carlos Eduardo\AppData\Local\Programs\ADI\LTspice\LTspice.exe"
asc = r"C:\Users\Carlos Eduardo\Documents\LTspice\ConfiguracaoCFP_SR_fix.asc"

csv_entrada = r"C:\Users\Carlos Eduardo\Documents\Workspace_VSCODE\Pesquisa\melhores_ganhos_por_corrente_configuracaoCFP_jfet20.csv"
csv_saida = r"C:\Users\Carlos Eduardo\Documents\Workspace_VSCODE\Pesquisa\slewrate_por_ganho_jfet20.csv"

fig_saida = r"C:\Users\Carlos Eduardo\Documents\Workspace_VSCODE\Pesquisa\slewrate_por_I1_jfet20.png"

runner = SimRunner(
    output_folder="./teste_py_lt_slew",
    simulator=lts
)

# ============================================================
# CONFIGURAÇÕES
# ============================================================

percentual_jfet = 0.01

# ============================================================
# CSV
# ============================================================

df = pd.read_csv(csv_entrada)
df = df.sort_values(["ganho_alvo", "I1_A"]).reset_index(drop=True)

resultados = []

numero = r"([-+]?[0-9]*\.?[0-9]+(?:[Ee][-+]?[0-9]+)?)"

# ============================================================
# VARREDURA
# ============================================================

for _, row in df.iterrows():

    ganho = float(row["ganho_alvo"])
    I1 = float(row["I1_A"])
    Rs = float(row["Rs_ohm"])
    Rd = float(row["Rd_ohm"])

    # Corrente por ramo
    I_ramo = I1 / 2

    # 20% da corrente do ramo passa pelo JFET
    I_jfet = percentual_jfet * I_ramo

    # I_JFET = 0.62/R13 = 0.62/R14
    R_jfet = 0.62 / I_jfet

    net = SpiceEditor(asc)

    net.set_component_value("I1", f"{I1:.12g}")

    net.set_component_value("Rs1d", f"{Rs:.12g}")
    net.set_component_value("Rs1e", f"{Rs:.12g}")

    net.set_component_value("Rd1d", f"{Rd:.12g}")
    net.set_component_value("Rd1e", f"{Rd:.12g}")

    net.set_component_value("R13", f"{R_jfet:.12g}")
    net.set_component_value("R14", f"{R_jfet:.12g}")

    try:
        raw_path, log_path = runner.run_now(net, timeout=1200)

        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            log = f.read()

        VLOW  = float(re.findall(rf"(?im)^\s*vlow\b.*?=\s*{numero}", log)[-1])
        VHIGH = float(re.findall(rf"(?im)^\s*vhigh\b.*?=\s*{numero}", log)[-1])
        V10   = float(re.findall(rf"(?im)^\s*v10\b.*?=\s*{numero}", log)[-1])
        V90   = float(re.findall(rf"(?im)^\s*v90\b.*?=\s*{numero}", log)[-1])

        T10 = float(re.findall(rf"(?im)^\s*t10\b.*?\bat\s+{numero}", log)[-1])
        T90 = float(re.findall(rf"(?im)^\s*t90\b.*?\bat\s+{numero}", log)[-1])

        TR = float(re.findall(rf"(?im)^\s*tr_10_90\b.*?=\s*{numero}", log)[-1])
        SR = float(re.findall(rf"(?im)^\s*sr_v_us\b.*?=\s*{numero}", log)[-1])

        resultados.append({
            "ganho_alvo": ganho,
            "I1_A": I1,
            "I1_mA": I1 * 1000,

            "I_ramo_mA": I_ramo * 1000,
            "percentual_jfet": percentual_jfet,
            "percentual_jfet_percent": percentual_jfet * 100,
            "I_jfet_mA": I_jfet * 1000,
            "R13_ohm": R_jfet,
            "R14_ohm": R_jfet,

            "Rs_ohm": Rs,
            "Rd_ohm": Rd,

            "Av_obtido": row["Av_obtido"],
            "erro": row["erro"],
            "THD": row["THD"],

            "VLOW_medido_V": VLOW,
            "VHIGH_medido_V": VHIGH,
            "V10_V": V10,
            "V90_V": V90,

            "T10_s": T10,
            "T90_s": T90,
            "tr_10_90_s": TR,

            "SR_subida_V_us": SR,
            "SR_abs_V_us": abs(SR)
        })

        print(
            f"Ganho = {ganho:6.2f} | "
            f"I1 = {I1*1000:8.4f} mA | "
            f"I_JFET = {I_jfet*1000:8.4f} mA | "
            f"R13=R14 = {R_jfet:10.3f} ohm | "
            f"Rs = {Rs:10.3f} ohm | "
            f"Rd = {Rd:10.3f} ohm | "
            f"SR = {SR:10.4f} V/us"
        )

    except Exception as e:
        print(
            f"Erro em ganho={ganho}, "
            f"I1={I1:.6f} A, "
            f"Rs={Rs:.4f}, "
            f"Rd={Rd:.4f}, "
            f"R13=R14={R_jfet:.4f} ohm -> {e}"
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
# PLOT: SLEW RATE vs I1
# ============================================================

plt.figure(figsize=(9, 6))

for ganho, grupo in df_saida.groupby("ganho_alvo"):

    grupo = grupo.sort_values("I1_mA")

    plt.plot(
        grupo["I1_mA"],
        grupo["SR_abs_V_us"],
        marker="o",
        linestyle="-",
        label=f"Av ≈ {ganho}"
    )

plt.title("Slew rate de subida vs corrente I1 - JFET com 20% da corrente")
plt.xlabel("I1 (mA)")
plt.ylabel("Slew rate de subida (V/us)")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig(fig_saida, dpi=600, bbox_inches="tight")
plt.show()

print(f"Figura salva em: {fig_saida}")