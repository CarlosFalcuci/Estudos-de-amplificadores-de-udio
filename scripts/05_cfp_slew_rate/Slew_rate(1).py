from PyLTSpice import SimRunner, SpiceEditor
import pandas as pd
import matplotlib.pyplot as plt
import re

# ============================================================
# CAMINHOS
# ============================================================

lts = r"C:\Users\Carlos Eduardo\AppData\Local\Programs\ADI\LTspice\LTspice.exe"
asc = r"C:\Users\Carlos Eduardo\Documents\LTspice\pestagio1.asc"

csv_entrada = r"C:\Users\Carlos Eduardo\Documents\Workspace_VSCODE\Pesquisa\melhores_ganhos_por_corrente.csv"
csv_saida = r"C:\Users\Carlos Eduardo\Documents\Workspace_VSCODE\Pesquisa\slewrate_por_ganho.csv"

fig_saida_1 = r"C:\Users\Carlos Eduardo\Documents\Workspace_VSCODE\Pesquisa\slewrate_por_I1.png"
fig_saida_2 = r"C:\Users\Carlos Eduardo\Documents\Workspace_VSCODE\Pesquisa\slewrate_por_Is_sobre_2.png"

runner = SimRunner(
    output_folder="./teste_py_lt_slew",
    simulator=lts
)

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

    net = SpiceEditor(asc)

    net.set_component_value("I1", f"{I1:.12g}")

    net.set_component_value("Rs1d", f"{Rs:.12g}")
    net.set_component_value("Rs1e", f"{Rs:.12g}")

    net.set_component_value("Rd1d", f"{Rd:.12g}")
    net.set_component_value("Rd1e", f"{Rd:.12g}")

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
        "Is_sobre_2_mA": (I1 * 1000)*2,
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
        f"I1 = {I1*1000:8.4f} mA | "
        f"Is/2 = {(I1*1000)/2:8.4f} mA | "
        f"Rs = {Rs:10.3f} ohm | "
        f"Rd = {Rd:10.3f} ohm | "
        f"SR = {SR:10.4f} V/us"
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
# PLOT 1: SLEW RATE vs I1
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

plt.title("Slew rate de subida vs corrente I1")
plt.xlabel("I1 (mA)")
plt.ylabel("Slew rate de subida (V/us)")
plt.xlim(0, 6)
plt.ylim(0, 20)
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig(fig_saida_1, dpi=600, bbox_inches="tight")
plt.show()

print(f"Figura salva em: {fig_saida_1}")

# ============================================================
# PLOT 2: SLEW RATE vs Is/2
# ============================================================

plt.figure(figsize=(9, 6))

for ganho, grupo in df_saida.groupby("ganho_alvo"):

    grupo = grupo.sort_values("Is_sobre_2_mA")

    plt.plot(
        grupo["Is_sobre_2_mA"],
        grupo["SR_abs_V_us"],
        marker="o",
        linestyle="-",
        label=f"Av ≈ {ganho}"
    )

plt.title("Slew rate de subida vs Is/2")
plt.xlabel("Is/2 (mA)")
plt.ylabel("Slew rate de subida (V/us)")
plt.xlim(0, 6)
plt.ylim(0, 20)
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig(fig_saida_2, dpi=600, bbox_inches="tight")
plt.show()

print(f"Figura salva em: {fig_saida_2}")