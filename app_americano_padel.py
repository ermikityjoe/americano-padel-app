
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Torneo Americano Pádel", layout="centered")

st.title("Torneo Americano Mixto - Pádel")
st.subheader("Domingo 30 de marzo - 4Winds")

# Paso 1: Ingresar nombres de jugadores
st.markdown("### Ingresar jugadores")
num_jugadores = 12
jugadores = []
for i in range(num_jugadores):
    jugador = st.text_input(f"Jugador {i+1}", key=f"jugador_{i}")
    if jugador:
        jugadores.append(jugador)

# Validar cantidad de jugadores
if len(jugadores) == num_jugadores:
    # Paso 2: Asignar parejas manualmente
    st.markdown("### Asignar parejas")
    parejas = []
    for i in range(0, num_jugadores, 2):
        pareja = f"{jugadores[i]} / {jugadores[i+1]}"
        parejas.append(pareja)

    st.success("Parejas asignadas:")
    for p in parejas:
        st.write(p)

    # Paso 3: Generar partidos (todos contra todos)
    st.markdown("### Ingresar resultados de los partidos")
    partidos = []
    for i in range(len(parejas)):
        for j in range(i+1, len(parejas)):
            partidos.append((parejas[i], parejas[j]))

    results = []
    for idx, (pareja1, pareja2) in enumerate(partidos):
        st.markdown(f"**{pareja1} vs {pareja2}**")
        col1, col2 = st.columns(2)
        with col1:
            score1 = st.number_input(f"{pareja1}", min_value=0, max_value=8, key=f"score1_{idx}")
        with col2:
            score2 = st.number_input(f"{pareja2}", min_value=0, max_value=8, key=f"score2_{idx}")
        results.append((pareja1, score1, pareja2, score2))

    # Paso 4: Calcular tabla de posiciones con G/E/P
    st.markdown("### Tabla de posiciones")
    tabla = {p: {"Games Ganados": 0, "Games Recibidos": 0, "G": 0, "E": 0, "P": 0} for p in parejas}
    enfrentamientos_directos = {}

    for pareja1, score1, pareja2, score2 in results:
        tabla[pareja1]["Games Ganados"] += score1
        tabla[pareja1]["Games Recibidos"] += score2
        tabla[pareja2]["Games Ganados"] += score2
        tabla[pareja2]["Games Recibidos"] += score1

        key = tuple(sorted([pareja1, pareja2]))
        enfrentamientos_directos[key] = (score1, score2)

        if score1 > score2:
            tabla[pareja1]["G"] += 1
            tabla[pareja2]["P"] += 1
        elif score2 > score1:
            tabla[pareja2]["G"] += 1
            tabla[pareja1]["P"] += 1
        else:
            tabla[pareja1]["E"] += 1
            tabla[pareja2]["E"] += 1

    df_tabla = pd.DataFrame.from_dict(tabla, orient="index")
    df_tabla["Diferencia"] = df_tabla["Games Ganados"] - df_tabla["Games Recibidos"]
    df_tabla = df_tabla.sort_values(by=["Games Ganados", "G", "Diferencia"], ascending=False)

    st.dataframe(df_tabla)
    st.caption("*Desempates: Games Ganados > Partidos Ganados > Enfrentamiento directo")
else:
    st.warning("Por favor, ingresa los 12 jugadores para continuar.")
