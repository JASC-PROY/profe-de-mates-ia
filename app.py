import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Profe de Mates IA", page_icon="✏️")
st.title("✏️ Profe de Mates IA")

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.warning("⚠️ Configura la clave GEMINI_API_KEY en los secretos de Streamlit para comenzar.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

tab1, tab2 = st.tabs(["📝 Generador de Problemas", "📷 Revisor de Divisiones"])

with tab1:
    st.header("Problemas Razonados")
    grado = st.selectbox("Selecciona el grado escolar:", ["1° - 2° Primaria", "3° - 4° Primaria", "5° - 6° Primaria"])
    tema = st.text_input("¿Qué le gusta al niño? (Ej. Dinosaurios, Minecraft, Fútbol):", "Videojuegos")
    
    if st.button("Generar problema"):
        prompt = f"Escribe un problema matemático para {grado} usando el tema {tema}. Dame el problema y la solución al final."
        with st.spinner("Creando problema..."):
            res = model.generate_content(prompt)
            st.write(res.text)

with tab2:
    st.header("Revisar División con Foto")
    foto = st.file_uploader("Sube la foto del cuaderno:", type=["jpg", "jpeg", "png"])
    
    if foto is not None:
        imagen = Image.open(foto)
        st.image(imagen, caption="Imagen cargada", width=300)
        
        if st.button("Revisar procedimiento"):
            prompt_vision = "Eres un maestro amigable. Revisa la división de la imagen. Dime si está correcta o en qué paso exacto se equivocó el niño."
            with st.spinner("Analizando foto..."):
                res = model.generate_content([prompt_vision, imagen])
                st.write(res.text)
