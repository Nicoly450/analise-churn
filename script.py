from os import system, name
system('cls') if name == 'nt' else system('clear')

import pandas as pd
from datetime import timedelta
import os

# 1) Lendo a base de dados
df = pd.read_csv("churn.csv", sep =",", encoding="utf-8")
df["data_pedido"] = pd.to_datetime(df["data_pedido"], errors="coerce")

print("Prévia dos dados:")
print(df.head())

# 2) Definindo data de referência (última compra registrada)
data_ref = df["data_pedido"].max()
limite_churn = data_ref - timedelta(days=90)

# 3) Última compra por cliente
ultimas = df.groupby("cliente", as_index=False)["data_pedido"].max()
ultimas["churn"] = ultimas["data_pedido"] < limite_churn

# 4) Calculando taxa de churn
churn_rate = ultimas["churn"].mean() * 100

# 5) Separando clientes ativos x churn
ativos = ultimas[~ultimas["churn"]]["cliente"]
churnados = ultimas[ultimas["churn"]]["cliente"]

df_ativos = df[df["cliente"].isin(ativos)]
df_churn = df[df["cliente"].isin(churnados)]

ticket_ativos = df_ativos.groupby("cliente")["valor"].mean().mean()
ticket_churn = df_churn.groupby("cliente")["valor"].mean().mean()

# 6) Criando pasta de resultados
os.makedirs("resultados", exist_ok=True)

# 7) Salvando resultados
pd.DataFrame([{"churn_rate": round(churn_rate, 2)}]) \
  .to_csv("resultados/churn_rate.csv", index=False)

ultimas[ultimas["churn"]] \
  .to_csv("resultados/clientes_inativos.csv", index=False)

pd.DataFrame([
    {"grupo": "ativos", "ticket_medio": round(ticket_ativos, 2)},
    {"grupo": "churn", "ticket_medio": round(ticket_churn, 2)}
]).to_csv("resultados/ticket_churn.csv", index=False)

# 8) Exibindo no terminal
print(f"\n📅 Data de referência: {data_ref.date()}")
print(f"📉 Taxa de churn: {churn_rate:.2f}%")
print(f"🎟️ Ticket médio (ativos): R$ {ticket_ativos:.2f}")
print(f"🎟️ Ticket médio (churn): R$ {ticket_churn:.2f}")
print("✅ Resultados salvos na pasta 'resultados/'")


# ------------------------
# GRÁFICOS (modo dark)
# ------------------------
import matplotlib.pyplot as plt
import os

os.makedirs("graficos", exist_ok=True)

# tema escuro global
plt.style.use("dark_background")
FIG_BG = "#0f1115"   
AX_BG  = "#0f1115"  

def _finish(filename):
    plt.tight_layout()
    plt.savefig(filename, dpi=140, facecolor=FIG_BG)
    plt.close()

# 1) Pizza - Ativos x Churn
qtd_churn = int(ultimas["churn"].sum())
qtd_ativos = int(len(ultimas) - qtd_churn)

plt.figure(figsize=(6, 6), facecolor=FIG_BG)
ax = plt.gca()
ax.set_facecolor(AX_BG)
plt.pie(
    [qtd_ativos, qtd_churn],
    labels=["Ativos", "Churn"],
    autopct="%.1f%%",
    startangle=90,
    colors=["#2ecc71", "#e67e22"],   
    wedgeprops={"linewidth": 1, "edgecolor": AX_BG},
    textprops={"fontsize": 11}
)
plt.title("Distribuição de Clientes (Ativos x Churn)", fontsize=12, pad=12)
_finish("graficos/churn_pizza_dark.png")

# 2) Barras - Ticket médio por grupo
plt.figure(figsize=(7, 4.2), facecolor=FIG_BG)
ax = plt.gca()
ax.set_facecolor(AX_BG)
ax.grid(axis="y", alpha=0.25, linestyle="--")
bars = plt.bar(
    ["ativos", "churn"],
    [ticket_ativos, ticket_churn],
    color=["#2e86de", "#e74c3c"]    
)
plt.title("Ticket Médio por Grupo", fontsize=12, pad=10)
plt.ylabel("Valor (R$)")
# rótulo no topo das barras
for b in bars:
    v = b.get_height()
    ax.text(b.get_x()+b.get_width()/2, v+1, f"R$ {v:.2f}", ha="center", va="bottom", fontsize=10)
_finish("graficos/ticket_barras_dark.png")

# 3) Linha - Evolução mensal de pedidos
df["mes"] = df["data_pedido"].dt.to_period("M").dt.to_timestamp()
serie = df.groupby("mes").size()

plt.figure(figsize=(8, 4.5), facecolor=FIG_BG)
ax = plt.gca()
ax.set_facecolor(AX_BG)
ax.grid(True, alpha=0.25, linestyle="--")
plt.plot(serie.index, serie.values, marker="o", linewidth=2, markersize=5, color="#00bcd4")
plt.title("Evolução Mensal de Pedidos", fontsize=12, pad=10)
plt.xlabel("Mês")
plt.ylabel("Qtd de Pedidos")
_finish("graficos/pedidos_linha_mensal_dark.png")
