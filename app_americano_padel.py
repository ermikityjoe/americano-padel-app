
import streamlit as st
import pandas as pd
from itertools import combinations
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Americano Pádel", layout="wide")

st.sidebar.header("Configuración del Torneo")
nombre_torneo = st.sidebar.text_input("Nombre del Americano", "Domingo 30 de marzo - 4Winds")
num_parejas = st.sidebar.number_input("Cantidad de parejas", min_value=2, max_value=20, value=6, step=1)
pistas = st.sidebar.number_input("Cantidad de pistas disponibles", min_value=1, max_value=10, value=3, step=1)

st.markdown(f"## Torneo: {nombre_torneo}")

num_jugadores = num_parejas * 2
jugadores = st.session_state.get("jugadores", [])

with st.expander("Paso 2: Ingresar nombres de jugadores"):
    for i in range(num_jugadores):
        jugador = st.text_input(f"Jugador {i+1}", key=f"jugador_{i}")
        if len(st.session_state.get(f"jugador_{i}", "")) > 0:
            if len(jugadores) < num_jugadores:
                jugadores.append(st.session_state[f"jugador_{i}"])

# Botón para crear torneo
if len(jugadores) == num_jugadores and not st.session_state.get("torneo_creado"):
    if st.button("🎾 Crear Torneo"):
        parejas = [f"{jugadores[i]} / {jugadores[i+1]}" for i in range(0, num_jugadores, 2)]
        partidos = list(combinations(parejas, 2))
        rondas = []
        ronda_actual = []
        ocupadas = set()

        for partido in partidos:
            p1, p2 = partido
            if p1 not in ocupadas and p2 not in ocupadas:
                ronda_actual.append(partido)
                ocupadas.update([p1, p2])
                if len(ronda_actual) == pistas:
                    rondas.append(ronda_actual)
                    ronda_actual = []
                    ocupadas = set()
        if ronda_actual:
            rondas.append(ronda_actual)

        rondas_con_pistas = []
        for ronda in rondas:
            ronda_con_pistas = []
            for i, partido in enumerate(ronda):
                pista = i + 1
                ronda_con_pistas.append((partido, pista))
            rondas_con_pistas.append(ronda_con_pistas)

        st.session_state.jugadores = jugadores
        st.session_state.parejas = parejas
        st.session_state.resultados = {}
        st.session_state.rondas_con_pistas = rondas_con_pistas
        st.session_state.torneo_creado = True

        # DEBUG - mostrar rondas generadas
        st.write('Debug - Total de rondas generadas:', len(st.session_state.rondas_con_pistas))
        for idx, ronda in enumerate(st.session_state.rondas_con_pistas):
            st.write(f'Ronda {idx + 1}:', ronda)

# Mostrar torneo
if st.session_state.get("torneo_creado"):
    st.success("Parejas asignadas:")
    for pareja in st.session_state.parejas:
        st.markdown(f"- {pareja}")

    ronda_labels = ["🏆 Clasificación"] + [f"R{i+1}" for i in range(len(st.session_state.rondas_con_pistas))]
    selected_tab = st.radio("Selecciona una ronda", ronda_labels, horizontal=True)

    if selected_tab == "🏆 Clasificación":
        st.header("Tabla de posiciones")
        tabla = {p: {"Games Ganados": 0, "Games Recibidos": 0, "G": 0, "E": 0, "P": 0} for p in st.session_state.parejas}
        for (p1, p2), (s1, s2) in st.session_state.resultados.items():
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

        if st.button("Descargar clasificación en PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Resultados del Torneo - {nombre_torneo}", ln=True, align="C")
            pdf.ln(10)
            for i, row in df_tabla.iterrows():
                texto = f"{i}: {row['Games Ganados']} GF, {row['Games Recibidos']} GC, G/E/P: {row['G']}/{row['E']}/{row['P']}"
                pdf.cell(200, 10, txt=texto, ln=True)

            pdf_buffer = BytesIO()
            pdf_output = pdf.output(dest='S').encode('latin1')
            pdf_buffer.write(pdf_output)
            pdf_buffer.seek(0)

            st.success("PDF generado correctamente")
            st.download_button(
                label="Descargar PDF",
                data=pdf_buffer,
                file_name=f"{nombre_torneo.replace(' ', '_')}_resultados.pdf",
                mime="application/pdf"
            )
    else:
        ronda_idx = int(selected_tab[1:]) - 1
        st.header(f"{selected_tab} - Resultados")
        for j, ((p1, p2), pista_num) in enumerate(st.session_state.rondas_con_pistas[ronda_idx]):
            st.markdown(f"#### Pista {pista_num}")
            col1, col2, col3 = st.columns([4, 1, 4])
            with col1:
                s1 = st.number_input(f"{p1}", min_value=0, max_value=8, key=f"{ronda_idx}_{j}_score1")
            with col2:
                st.markdown("<h5 style='text-align: center;'>VS</h5>", unsafe_allow_html=True)
            with col3:
                s2 = st.number_input(f"{p2}", min_value=0, max_value=8, key=f"{ronda_idx}_{j}_score2")
            st.session_state.resultados[(p1, p2)] = (s1, s2)
