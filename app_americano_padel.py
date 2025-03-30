
import streamlit as st
import pandas as pd
from itertools import combinations
import random

st.set_page_config(layout="wide")

# Configuración inicial
if "configurado" not in st.session_state:
    st.session_state.configurado = False
    st.session_state.nombres = []
    st.session_state.partidos_jugados = set()
    st.session_state.rondas = []
    st.session_state.resultados = {}
    st.session_state.tabla = pd.DataFrame()

st.title("Torneo Americano de Pádel")

# Paso 1: Configuración
st.sidebar.header("Configuración del Torneo")
nombre_torneo = st.sidebar.text_input("Nombre del Americano", "Domingo 30 de marzo - 4Winds")
cantidad_parejas = st.sidebar.number_input("Cantidad de parejas", min_value=2, max_value=20, step=1, value=6)
cantidad_pistas = st.sidebar.number_input("Cantidad de pistas disponibles", min_value=1, max_value=10, step=1, value=3)

# Paso 2: Ingreso de jugadores
if not st.session_state.configurado:
    st.subheader("Paso 2: Ingresar nombres de jugadores")
    with st.form("form_jugadores"):
        nombres = []
        for i in range(int(cantidad_parejas) * 2):
            nombre = st.text_input(f"Jugador {i+1}", key=f"jugador_{i}")
            nombres.append(nombre)
        submitted = st.form_submit_button("🎾 Crear Torneo")
        if submitted:
            st.session_state.nombres = nombres
            parejas = [(nombres[i], nombres[i+1]) for i in range(0, len(nombres), 2)]
            st.session_state.parejas = parejas
            st.session_state.nombres_parejas = [f"{a} / {b}" for a, b in parejas]
            st.session_state.tabla = pd.DataFrame({
                "Pareja": st.session_state.nombres_parejas,
                "Games Ganados": 0,
                "Games Recibidos": 0,
                "G": 0,
                "E": 0,
                "P": 0,
                "Diferencia": 0
            }).set_index("Pareja")

            # Generar rondas
            partidos_totales = list(combinations(range(len(parejas)), 2))
            random.shuffle(partidos_totales)
            rondas = []
            intentos = 0
            max_intentos = 500

            while partidos_totales and len(rondas) < len(parejas) - 1:
                ronda = []
                parejas_usadas = set()
                for p in partidos_totales:
                    if p[0] in parejas_usadas or p[1] in parejas_usadas:
                        continue
                    ronda.append(p)
                    parejas_usadas.add(p[0])
                    parejas_usadas.add(p[1])
                    if len(ronda) == cantidad_pistas:
                        break
                if len(ronda) == cantidad_pistas:
                    rondas.append(ronda)
                    for p in ronda:
                        partidos_totales.remove(p)
                else:
                    intentos += 1
                    if intentos > max_intentos:
                        st.error("❌ No se pudieron generar todas las rondas sin repetir enfrentamientos.")
                        break

            st.session_state.rondas = rondas
            st.session_state.resultados = {
                f"R{i+1}": {j: [0, 0] for j in range(len(ronda))} for i, ronda in enumerate(rondas)
            }
            st.session_state.configurado = True
            st.experimental_rerun()

# Mostrar el torneo
if st.session_state.configurado:
    st.success("✅ Torneo creado exitosamente.")
    st.subheader("Parejas asignadas:")
    for pareja in st.session_state.nombres_parejas:
        st.markdown(f"- {pareja}")

    st.markdown("---")
    st.subheader("Fixture")

    ronda_seleccionada = st.radio("Selecciona una ronda", ["🏆 Clasificación"] + [f"R{i+1}" for i in range(len(st.session_state.rondas))])

    if ronda_seleccionada == "🏆 Clasificación":
        st.subheader("Tabla de posiciones")
        st.dataframe(st.session_state.tabla)
    else:
        idx = int(ronda_seleccionada[1:]) - 1
        ronda = st.session_state.rondas[idx]
        resultados = st.session_state.resultados[ronda_seleccionada]

        st.subheader(f"{ronda_seleccionada} - Resultados")
        for i, (p1, p2) in enumerate(ronda):
            col1, col2, col3 = st.columns([4, 1, 4])
            nombre1 = st.session_state.nombres_parejas[p1]
            nombre2 = st.session_state.nombres_parejas[p2]
            with col1:
                resultados[i][0] = st.number_input(f"{nombre1}", min_value=0, key=f"{ronda_seleccionada}_{i}_1", value=resultados[i][0])
            with col2:
                st.markdown("### VS")
            with col3:
                resultados[i][1] = st.number_input(f"{nombre2}", min_value=0, key=f"{ronda_seleccionada}_{i}_2", value=resultados[i][1])
