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
# GRÁFICOS (Matplotlib)
# ------------------------
import matplotlib.pyplot as plt

os.makedirs("graficos", exist_ok=True)

# 1) Pizza - distribuição Ativos x Churn
qtd_churn = int(ultimas["churn"].sum())
qtd_ativos = int(len(ultimas) - qtd_churn)

plt.figure(figsize=(6, 6))
plt.pie([qtd_ativos, qtd_churn],
        labels=["Ativos", "Churn"],
        autopct="%.1f%%",
        startangle=90)
plt.title("Distribuição de Clientes (Ativos x Churn)")
plt.savefig("graficos/churn_pizza.png")
plt.close()

# 2) Barras - Ticket médio por grupo
plt.figure(figsize=(6, 4))
plt.bar(["ativos", "churn"], [ticket_ativos, ticket_churn])
plt.title("Ticket Médio por Grupo")
plt.ylabel("Valor (R$)")
plt.savefig("graficos/ticket_barras.png")
plt.close()

# 3) Linha - Evolução mensal de pedidos
df["mes"] = df["data_pedido"].dt.to_period("M").dt.to_timestamp()
serie = df.groupby("mes").size()

plt.figure(figsize=(8, 4))
plt.plot(serie.index, serie.values, marker="o", color="blue")
plt.title("Evolução Mensal de Pedidos")
plt.xlabel("Mês")
plt.ylabel("Qtd de Pedidos")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("graficos/pedidos_linha_mensal.png", dpi=120)
plt.close()
