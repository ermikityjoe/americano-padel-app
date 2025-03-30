
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Torneo Americano Pádel", layout="centered")

st.title("Torneo Americano Mixto - Pádel")
st.subheader("Domingo 30 de marzo - 4Winds")

parejas = [
    "Kari / Polo",
    "Diana / Alvaro",
    "Jaime / Lina",
    "María / Félix",
    "Andrea A / Joel",
    "Mary / César"
]

partidos = [
    # Ronda 1
    ("Ronda 1", "Kari / Polo", "Diana / Alvaro"),
    ("Ronda 1", "Jaime / Lina", "María / Félix"),
    ("Ronda 1", "Andrea A / Joel", "Mary / César"),
    # Ronda 2
    ("Ronda 2", "Kari / Polo", "Jaime / Lina"),
    ("Ronda 2", "Diana / Alvaro", "Andrea A / Joel"),
    ("Ronda 2", "María / Félix", "Mary / César"),
    # Ronda 3
    ("Ronda 3", "Kari / Polo", "María / Félix"),
    ("Ronda 3", "Jaime / Lina", "Mary / César"),
    ("Ronda 3", "Diana / Alvaro", "Andrea A / Joel"),
    # Ronda 4
    ("Ronda 4", "Kari / Polo", "Andrea A / Joel"),
    ("Ronda 4", "Diana / Alvaro", "Mary / César"),
    ("Ronda 4", "Jaime / Lina", "María / Félix"),
    # Ronda 5
    ("Ronda 5", "Kari / Polo", "Mary / César"),
    ("Ronda 5", "Diana / Alvaro", "María / Félix"),
    ("Ronda 5", "Jaime / Lina", "Andrea A / Joel"),
]

st.markdown("### Ingresar resultados")

# Inicializar un DataFrame para los resultados
results = []

for i, (ronda, pareja1, pareja2) in enumerate(partidos):
    st.markdown(f"**{ronda} - {pareja1} vs {pareja2}**")
    col1, col2 = st.columns(2)
    with col1:
        score1 = st.number_input(f"{pareja1}", min_value=0, max_value=8, key=f"score1_{i}")
    with col2:
        score2 = st.number_input(f"{pareja2}", min_value=0, max_value=8, key=f"score2_{i}")
    results.append((pareja1, score1, pareja2, score2))

# Calcular tabla de posiciones
st.markdown("### Tabla de posiciones")
tabla = {p: {"Games Ganados": 0, "Games Recibidos": 0} for p in parejas}

for pareja1, score1, pareja2, score2 in results:
    tabla[pareja1]["Games Ganados"] += score1
    tabla[pareja1]["Games Recibidos"] += score2
    tabla[pareja2]["Games Ganados"] += score2
    tabla[pareja2]["Games Recibidos"] += score1

df_tabla = pd.DataFrame.from_dict(tabla, orient="index")
df_tabla["Diferencia"] = df_tabla["Games Ganados"] - df_tabla["Games Recibidos"]
df_tabla = df_tabla.sort_values(by=["Games Ganados", "Diferencia"], ascending=False)

st.dataframe(df_tabla)
