from PyLTSpice import SimRunner, SpiceEditor
import re

# ============================================================
# CAMINHOS
# ============================================================

lts = r"C:\Users\Carlos Eduardo\AppData\Local\Programs\ADI\LTspice\LTspice.exe"
asc = r"C:\Users\Carlos Eduardo\Documents\LTspice\pestagio1.asc"

runner = SimRunner(
    output_folder="./teste_py_lt_slew_unico",
    simulator=lts
)

# ============================================================
# VALORES DO TESTE
# ============================================================

I1 = 0.1000e-3
Rs = 31609.195
Rd = 400000.000

# ============================================================
# EDITA APENAS OS COMPONENTES
# ============================================================

net = SpiceEditor(asc)

net.set_component_value("I1", f"{I1:.12g}")

net.set_component_value("Rs1d", f"{Rs:.12g}")
net.set_component_value("Rs1e", f"{Rs:.12g}")

net.set_component_value("Rd1d", f"{Rd:.12g}")
net.set_component_value("Rd1e", f"{Rd:.12g}")

print("Valores aplicados:")
print(f"I1   = {I1} A")
print(f"Rs1d = {Rs} ohm")
print(f"Rs1e = {Rs} ohm")
print(f"Rd1d = {Rd} ohm")
print(f"Rd1e = {Rd} ohm")

# ============================================================
# RODA A SIMULAÇÃO
# ============================================================

raw_path, log_path = runner.run_now(net, timeout=1200)

print("\nRAW:", raw_path)
print("LOG:", log_path)

# ============================================================
# LÊ O LOG
# ============================================================

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    log = f.read()

numero = r"([-+]?[0-9]*\.?[0-9]+(?:[Ee][-+]?[0-9]+)?)"

VLOW  = float(re.findall(rf"(?im)^\s*vlow\b.*?=\s*{numero}", log)[-1])
VHIGH = float(re.findall(rf"(?im)^\s*vhigh\b.*?=\s*{numero}", log)[-1])
V10   = float(re.findall(rf"(?im)^\s*v10\b.*?=\s*{numero}", log)[-1])
V90   = float(re.findall(rf"(?im)^\s*v90\b.*?=\s*{numero}", log)[-1])

T10 = float(re.findall(rf"(?im)^\s*t10\b.*?\bat\s+{numero}", log)[-1])
T90 = float(re.findall(rf"(?im)^\s*t90\b.*?\bat\s+{numero}", log)[-1])

TR = float(re.findall(rf"(?im)^\s*tr_10_90\b.*?=\s*{numero}", log)[-1])
SR = float(re.findall(rf"(?im)^\s*sr_v_us\b.*?=\s*{numero}", log)[-1])

# ============================================================
# MOSTRA RESULTADOS
# ============================================================

print("\nResultados extraídos do log:")
print(f"VLOW      = {VLOW:.6f} V")
print(f"VHIGH     = {VHIGH:.6f} V")
print(f"V10       = {V10:.6f} V")
print(f"V90       = {V90:.6f} V")
print(f"T10       = {T10:.12f} s")
print(f"T90       = {T90:.12f} s")
print(f"TR_10_90  = {TR:.12e} s")
print(f"SR_V_US   = {SR:.6f} V/us")

print("\n===== FINAL DO LOG =====")
print("\n".join(log.splitlines()[-80:]))
print("===== FIM DO LOG =====")