from PyLTSpice import SimRunner, SpiceEditor
import pandas as pd
import matplotlib.pyplot as plt
import os
import re

lts = r"C:\Users\Carlos Eduardo\AppData\Local\Programs\ADI\LTspice\LTspice.exe"
runner = SimRunner(output_folder='./teste_py_lt_ac', simulator=lts)

asc = r"C:\Users\Carlos Eduardo\Documents\LTspice\ConfiguracaoCFP_FC_fix.asc"
csv_file = r"C:\Users\Carlos Eduardo\Documents\Workspace_VSCODE\Pesquisa\melhores_ganhos_por_corrente.csv"
csv_saida = r"C:\Users\Carlos Eduardo\Documents\Workspace_VSCODE\Pesquisa\fh_por_ganho.csv"

if not os.path.exists(csv_file):
    raise FileNotFoundError(f"Arquivo CSV não encontrado: {csv_file}")

df = pd.read_csv(csv_file)
df = df.sort_values(["ganho_alvo", "I1_A"]).reset_index(drop=True)
ganhos = sorted(df["ganho_alvo"].unique())

def extrair_fh_do_arquivo_log(log_path):
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        texto = f.read()

    # Procura linha do tipo:
    # fh: mag(V(vout))=gmax/sqrt(2) AT 30871.5857137
    padrao = r'^\s*fh:.*?\bAT\s+([0-9Ee+\-\.]+)'
    m = re.search(padrao, texto, flags=re.MULTILINE | re.IGNORECASE)

    if m:
        return float(m.group(1))

    raise ValueError(f"Não foi possível extrair fh do log: {log_path}")

net_editor = SpiceEditor(asc)

resultados_plot = {}
resultados_csv = []

for ganho in ganhos:
    df_g = df[df["ganho_alvo"] == ganho].copy()

    correntes_mA = []
    fhs = []

    print(f"\n========== GANHO ALVO = {ganho} ==========\n")

    for _, row in df_g.iterrows():
        I1 = float(row["I1_A"])
        Rs = float(row["Rs_ohm"])

        # mantém polarização dos Rd em 20 V
        Rd = 20 / (I1 / 2)

        net_editor.set_component_value("I1", I1)
        net_editor.set_component_value("Rs1d", str(Rs))
        net_editor.set_component_value("Rs1e", str(Rs))
        net_editor.set_component_value("Rd1d", str(Rd))
        net_editor.set_component_value("Rd1e", str(Rd))

        try:
            raw_path, log_path = runner.run_now(net_editor)

            fh = extrair_fh_do_arquivo_log(log_path)

            correntes_mA.append(I1 * 1000)
            fhs.append(fh)

            resultados_csv.append({
                "ganho_alvo": ganho,
                "I1_A": I1,
                "I1_mA": I1 * 1000,
                "Rs_ohm": Rs,
                "Rd_ohm": Rd,
                "fh_Hz": fh
            })

            print(
                f"I1 = {I1*1000:8.4f} mA | "
                f"Rs = {Rs:10.4f} ohm | "
                f"Rd = {Rd:10.4f} ohm | "
                f"fh = {fh:12.4f} Hz"
            )

        except Exception as e:
            print(
                f"Erro em ganho={ganho}, "
                f"I1={I1:.6f} A, Rs={Rs:.4f}, Rd={Rd:.4f} -> {e}"
            )

    resultados_plot[ganho] = {
        "correntes_mA": correntes_mA,
        "fhs": fhs
    }

df_saida = pd.DataFrame(resultados_csv)
df_saida.to_csv(csv_saida, index=False, encoding="utf-8-sig")

print(f"\nCSV salvo em: {csv_saida}")

plt.figure(figsize=(9, 6))

for ganho in ganhos:
    x = resultados_plot[ganho]["correntes_mA"]
    y = resultados_plot[ganho]["fhs"]
    plt.plot(x, y, marker='o', linestyle='-', label=f'Av ≈ {ganho}')

plt.title("Frequência de corte superior vs corrente")
plt.xlabel("I1 (mA)")
plt.ylabel("fh (Hz)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()