
import streamlit as st
import pandas as pd
from itertools import combinations
from fpdf import FPDF

st.set_page_config(page_title="Torneo Americano Pádel", layout="wide")

st.title("Torneo Americano Mixto - Pádel")

# Paso 1: Información inicial del torneo
st.sidebar.header("Configuración del Torneo")
nombre_torneo = st.sidebar.text_input("Nombre del Americano", "Domingo 30 de marzo - 4Winds")
num_parejas = st.sidebar.number_input("Cantidad de parejas", min_value=2, max_value=20, value=6, step=1)
pistas = st.sidebar.number_input("Cantidad de pistas disponibles", min_value=1, max_value=10, value=3, step=1)

st.subheader(nombre_torneo)

num_jugadores = num_parejas * 2
jugadores = []

with st.expander("Paso 2: Ingresar nombres de jugadores"):
    for i in range(num_jugadores):
        jugador = st.text_input(f"Jugador {i+1}", key=f"jugador_{i}")
        if jugador:
            jugadores.append(jugador)

if len(jugadores) == num_jugadores:
    # Asignar parejas en orden
    parejas = [f"{jugadores[i]} / {jugadores[i+1]}" for i in range(0, num_jugadores, 2)]

    st.success("Parejas asignadas:")
    st.write(parejas)

    # Generar partidos todos contra todos
    partidos = list(combinations(parejas, 2))
    total_rondas = (len(partidos) + pistas - 1) // pistas
    rondas = [[] for _ in range(total_rondas)]

    # Asignar partidos a rondas
    for idx, partido in enumerate(partidos):
        ronda_index = idx % total_rondas
        rondas[ronda_index].append(partido)

    resultados = {}

    tabs = st.tabs([f"Ronda {i+1}" for i in range(total_rondas)] + ["Clasificación"])

    for i, tab in enumerate(tabs[:-1]):
        with tab:
            st.header(f"Ronda {i+1}")
            for j, (p1, p2) in enumerate(rondas[i]):
                st.markdown(f"### {p1} ⬅️ vs ➡️ {p2}")
                col1, col2 = st.columns([1, 1])
                with col1:
                    s1 = st.number_input("Score", min_value=0, max_value=8, key=f"{i}_{j}_score1")
                with col2:
                    s2 = st.number_input("Score", min_value=0, max_value=8, key=f"{i}_{j}_score2")
                resultados[(p1, p2)] = (s1, s2)

    # Clasificación
    with tabs[-1]:
        st.header("Tabla de posiciones")
        tabla = {p: {"Games Ganados": 0, "Games Recibidos": 0, "G": 0, "E": 0, "P": 0} for p in parejas}
        for (p1, p2), (s1, s2) in resultados.items():
            tabla[p1]["Games Ganados"] += s1
            tabla[p1]["Games Recibidos"] += s2
            tabla[p2]["Games Ganados"] += s2
            tabla[p2]["Games Recibidos"] += s1
            if s1 > s2:
                tabla[p1]["G"] += 1
                tabla[p2]["P"] += 1
            elif s2 > s1:
                tabla[p2]["G"] += 1
                tabla[p1]["P"] += 1
            else:
                tabla[p1]["E"] += 1
                tabla[p2]["E"] += 1

        df_tabla = pd.DataFrame.from_dict(tabla, orient="index")
        df_tabla["Diferencia"] = df_tabla["Games Ganados"] - df_tabla["Games Recibidos"]
        df_tabla = df_tabla.sort_values(by=["Games Ganados", "G", "Diferencia"], ascending=False)

        st.dataframe(df_tabla)

        # Exportar resultados
        if st.button("Descargar clasificación en PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Resultados - {nombre_torneo}", ln=True, align="C")
            pdf.ln(10)
            for i, row in df_tabla.iterrows():
                texto = f"{i}: {row['Games Ganados']} GF, {row['Games Recibidos']} GC, G/E/P: {row['G']}/{row['E']}/{row['P']}"
                pdf.cell(200, 10, txt=texto, ln=True)
            pdf_output = f"/mnt/data/{nombre_torneo.replace(' ', '_')}_resultados.pdf"
            pdf.output(pdf_output)
            st.success("PDF generado correctamente")
            st.markdown(f"[Descargar PDF]({pdf_output})")
else:
    st.warning("Por favor, ingresa todos los jugadores para continuar.")
