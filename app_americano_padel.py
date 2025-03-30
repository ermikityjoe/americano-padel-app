
import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

# Fixture Round Robin predefinido para 6 parejas
def generar_fixtures_6_parejas():
    rondas = [
        [("A", "F"), ("B", "E"), ("C", "D")],
        [("A", "E"), ("F", "D"), ("B", "C")],
        [("A", "D"), ("E", "C"), ("F", "B")],
        [("A", "C"), ("D", "B"), ("E", "F")],
        [("A", "B"), ("C", "F"), ("D", "E")]
    ]
    return rondas

st.set_page_config(page_title="Torneo Americano Padel", layout="wide")

if "resultados" not in st.session_state:
    st.session_state.resultados = {}

st.title("Organizador Torneo Americano de Pádel")

st.sidebar.header("Configuración del Torneo")
nombre_torneo = st.sidebar.text_input("Nombre del Americano", value="Domingo 30 de marzo - 4Winds")
num_parejas = st.sidebar.number_input("Cantidad de parejas", min_value=6, max_value=6, step=1, value=6)

jugadores = []
for i in range(num_parejas * 2):
    jugador = st.text_input(f"Jugador {i+1}", key=f"jugador_{i}")
    jugadores.append(jugador)

if st.button("🎾 Crear Torneo"):
    parejas = [(jugadores[i], jugadores[i+1]) for i in range(0, len(jugadores), 2)]
    nombres_parejas = [f"{p[0]} / {p[1]}" for p in parejas]
    fixture = generar_fixtures_6_parejas()
    st.session_state.parejas = nombres_parejas
    st.session_state.fixture = fixture
    st.session_state.resultados = {}

if "fixture" in st.session_state:
    fixture = st.session_state.fixture
    parejas = st.session_state.parejas

    st.success("Parejas asignadas:")
    for p in parejas:
        st.markdown(f"- {p}")

    opciones = ["📋 Fixture", "🏆 Clasificación"] + [f"R{i+1}" for i in range(len(fixture))]
    seleccion = st.radio("Selecciona una ronda", opciones, horizontal=True)

    
    if seleccion == "📋 Fixture":
        st.header("📋 Fixture completo del torneo")
        etiquetas = ["A", "B", "C", "D", "E", "F"]
        map_parejas = dict(zip(etiquetas, parejas))
        fixture_nombres = [
            [(map_parejas[a], map_parejas[b]) for a, b in [
                ("A", "F"), ("B", "E"), ("C", "D")
            ]],
            [(map_parejas[a], map_parejas[b]) for a, b in [
                ("A", "E"), ("F", "D"), ("B", "C")
            ]],
            [(map_parejas[a], map_parejas[b]) for a, b in [
                ("A", "D"), ("E", "C"), ("F", "B")
            ]],
            [(map_parejas[a], map_parejas[b]) for a, b in [
                ("A", "C"), ("D", "B"), ("E", "F")
            ]],
            [(map_parejas[a], map_parejas[b]) for a, b in [
                ("A", "B"), ("C", "F"), ("D", "E")
            ]]
        ]
        for i, ronda in enumerate(fixture_nombres):
            st.markdown(f"### Ronda {i+1}")
            for p1, p2 in ronda:
                st.markdown(f"- {p1} vs {p2}")
    elif seleccion == "🏆 Clasificación":

        tabla = pd.DataFrame(index=parejas, columns=["Games Ganados", "Games Recibidos", "G", "E", "P", "Diferencia"])
        tabla.fillna(0, inplace=True)
        for i, ronda in enumerate(fixture):
            for j, match in enumerate(ronda):
                key1 = f"r{i}_m{j}_1"
                key2 = f"r{i}_m{j}_2"
                g1 = st.session_state.resultados.get(key1, 0)
                g2 = st.session_state.resultados.get(key2, 0)
                p1 = match[0]
                p2 = match[1]
                tabla.at[p1, "Games Ganados"] += g1
                tabla.at[p1, "Games Recibidos"] += g2
                tabla.at[p2, "Games Ganados"] += g2
                tabla.at[p2, "Games Recibidos"] += g1
                if g1 > g2:
                    tabla.at[p1, "G"] += 1
                    tabla.at[p2, "P"] += 1
                elif g1 < g2:
                    tabla.at[p2, "G"] += 1
                    tabla.at[p1, "P"] += 1
                else:
                    tabla.at[p1, "E"] += 1
                    tabla.at[p2, "E"] += 1
        tabla["Diferencia"] = tabla["Games Ganados"] - tabla["Games Recibidos"]
        tabla_ordenada = tabla.sort_values(by=["Games Ganados", "G"], ascending=False)
        st.subheader("Tabla de posiciones")
        st.dataframe(tabla_ordenada)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Clasificación - {nombre_torneo}", ln=True)

        for idx, row in tabla_ordenada.iterrows():
            linea = f"{idx}: {row['Games Ganados']} ganados, {row['Games Recibidos']} recibidos, G:{row['G']} E:{row['E']} P:{row['P']}"
            pdf.cell(200, 10, txt=linea, ln=True)

        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)

        st.download_button("Descargar clasificación en PDF", data=pdf_buffer, file_name="clasificacion.pdf", mime="application/pdf")

    else:
        ronda_idx = int(seleccion[1:]) - 1
        st.header(f"{seleccion} - Resultados")
        partidos = fixture[ronda_idx]
        for idx, match in enumerate(partidos):
            col1, col2, col3 = st.columns([4, 1, 4])
            key1 = f"r{ronda_idx}_m{idx}_1"
            key2 = f"r{ronda_idx}_m{idx}_2"
            with col1:
                g1 = st.number_input(match[0], min_value=0, max_value=8, key=key1)
                st.session_state.resultados[key1] = g1
            with col2:
                st.markdown("## VS")
            with col3:
                g2 = st.number_input(match[1], min_value=0, max_value=8, key=key2)
                st.session_state.resultados[key2] = g2
