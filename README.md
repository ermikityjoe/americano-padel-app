
# Torneo Americano de Pádel - App Streamlit

Esta es una aplicación web para organizar y llevar el control de torneos tipo **Americano** de pádel.

## Funcionalidades

- Registro de participantes y asignación automática de parejas.
- Configuración personalizada: nombre del torneo, cantidad de parejas y pistas disponibles.
- Generación automática de rondas sin repetir parejas en una misma ronda.
- Ingreso de resultados por pista y ronda.
- Clasificación en tiempo real según juegos ganados, recibidos, partidos ganados, empatados y perdidos.
- Descarga de resultados en PDF.

## Cómo usar

1. Clona este repositorio o súbelo a tu cuenta de GitHub.
2. Asegúrate de que el archivo principal se llama `app.py` o configura ese nombre en [Streamlit Cloud](https://streamlit.io/cloud).
3. Sube los siguientes archivos:
   - `app_americano_padel_final_todas_las_rondas.py` (renómbralo como `app.py` si deseas)
   - `requirements.txt`
4. Inicia tu app en Streamlit Cloud.

## Requisitos

- Python 3.7+
- Streamlit
- Pandas
- FPDF

Instalación local:
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

Desarrollado con cariño por Polo y Chatty.
