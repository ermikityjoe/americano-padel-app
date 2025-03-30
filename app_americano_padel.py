
import streamlit as st
import pandas as pd
from itertools import combinations
from fpdf import FPDF
from io import BytesIO

st.set_page_config(layout="wide")

# Título
st.title("Torneo Americano de Pádel")

# Inicialización de sesión
if "torneo_creado" not in st.session_state:
    st.session_state.torneo_creado = False

if "resultados" not in st.session_state:
    st.session_state.resultados = {}

# Paso 1: Configuración
st.sidebar.header("Configuración del Torneo")
nombre_torneo = st.sidebar.text_input("Nombre del Americano", "Torneo Mixto")
num_parejas = st.sidebar.number_input("Cantidad de parejas", min_value=2, max_value=12, value=6, step=2)
num_pistas = st.sidebar.number_input("Cantidad de pistas disponibles", min_value=1, max_value=6, value=3, step=1)

# Paso 2: Ingreso de jugadores
if not st.session_state.torneo_creado:
    st.subheader("Paso 2: Ingresar nombres de jugadores")
    jugadores = []
    for i in range(num_parejas * 2):
        jugador = st.text_input(f"Jugador {i+1}", key=f"jugador_{i}")
        jugadores.append(jugador.strip())

    if st.button("🎾 Crear Torneo"):
        # Crear parejas
        parejas = [f"{jugadores[i]} / {jugadores[i+1]}" for i in range(0, len(jugadores), 2)]
        st.session_state.parejas = parejas

        # Generar todas las combinaciones posibles de partidos entre parejas
        partidos_posibles = list(combinations(range(len(parejas)), 2))

        # Generar 5 rondas con 3 partidos cada una (total 15 partidos sin repeticiones)
        rondas = []
        partidos_usados = set()
        while len(rondas) < len(parejas) - 1:
            ronda = []
            parejas_usadas = set()
            for p in partidos_posibles:
                if p in partidos_usados:
                    continue
                if p[0] in parejas_usadas or p[1] in parejas_usadas:
                    continue
                ronda.append(p)
                parejas_usadas.update(p)
                partidos_usados.add(p)
                if len(ronda) == num_pistas:
                    break
            if len(ronda) == num_pistas:
                rondas.append(ronda)

        st.session_state.rondas = rondas
        st.session_state.torneo_creado = True
        st.rerun()

# Paso 3: Mostrar torneo
if st.session_state.torneo_creado:
    st.success("Torneo creado con éxito")
    parejas = st.session_state.parejas
    rondas = st.session_state.rondas

    st.markdown("### Parejas asignadas:")
    for pareja in parejas:
        st.markdown(f"- {pareja}")

    # Selección de ronda o clasificación
    opcion = st.radio("Selecciona una ronda", ["🏆 Clasificación"] + [f"R{i+1}" for i in range(len(rondas))])

    if opcion == "🏆 Clasificación":
        tabla = pd.DataFrame(index=parejas, columns=["Games Ganados", "Games Recibidos", "G", "E", "P", "Diferencia"]).fillna(0)

        # Calcular tabla
        for i, ronda in enumerate(rondas):
            for partido in ronda:
                p1, p2 = partido
                key1 = f"r{i}_p{p1}"
                key2 = f"r{i}_p{p2}"
                g1 = st.session_state.resultados.get(key1, 0)
                g2 = st.session_state.resultados.get(key2, 0)

                tabla.at[parejas[p1], "Games Ganados"] += g1
                tabla.at[parejas[p1], "Games Recibidos"] += g2
                tabla.at[parejas[p2], "Games Ganados"] += g2
                tabla.at[parejas[p2], "Games Recibidos"] += g1

                if g1 > g2:
                    tabla.at[parejas[p1], "G"] += 1
                    tabla.at[parejas[p2], "P"] += 1
                elif g2 > g1:
                    tabla.at[parejas[p2], "G"] += 1
                    tabla.at[parejas[p1], "P"] += 1
                else:
                    tabla.at[parejas[p1], "E"] += 1
                    tabla.at[parejas[p2], "E"] += 1

        tabla["Diferencia"] = tabla["Games Ganados"] - tabla["Games Recibidos"]
        tabla_ordenada = tabla.sort_values(by=["G", "Diferencia", "Games Ganados"], ascending=False)

        st.subheader("Tabla de posiciones")
        st.dataframe(tabla_ordenada)

        # Descargar PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Clasificación - {nombre_torneo}", ln=True)
        pdf.ln(10)
        for i, row in tabla_ordenada.iterrows():
            linea = f"{i}: {row['G']}G - {row['E']}E - {row['P']}P | Games: {row['Games Ganados']} / {row['Games Recibidos']}"
            pdf.cell(200, 10, txt=linea, ln=True)

        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)

        st.download_button("📄 Descargar clasificación en PDF", data=buffer, file_name=f"{nombre_torneo}.pdf", mime="application/pdf")
    else:
        idx = int(opcion[1:]) - 1
        st.subheader(f"{opcion} - Resultados")
        for i, partido in enumerate(rondas[idx]):
            p1, p2 = partido
            col1, colv, col2 = st.columns([5, 1, 5])
            with col1:
                st.session_state.resultados[f"r{idx}_p{p1}"] = st.number_input(parejas[p1], min_value=0, key=f"r{idx}_p{p1}")
            with colv:
                st.markdown("### VS")
            with col2:
                st.session_state.resultados[f"r{idx}_p{p2}"] = st.number_input(parejas[p2], min_value=0, key=f"r{idx}_p{p2}")
