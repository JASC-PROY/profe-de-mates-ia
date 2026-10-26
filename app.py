import streamlit as st
from google import genai
from google.genai.errors import APIError
from PIL import Image

st.set_page_config(page_title="Profe de Mates IA", page_icon="✏️", layout="centered")
st.title("✏️ Profe de Mates IA")

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ No se encontró GEMINI_API_KEY en los Secrets de Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)

def generar_con_respaldo(contents):
    modelos = ['gemini-3.8-flash', 'gemini-3.5-flash', 'gemini-3.5-flash-lite']
    ultimo_error = None
    
    for mod in modelos:
        try:
            response = client.models.generate_content(
                model=mod,
                contents=contents
            )
            return response.text
        except APIError as e:
            ultimo_error = e
            continue
        except Exception as e:
            ultimo_error = e
            continue
            
    raise ultimo_error

tab1, tab2 = st.tabs(["📝 Generador de Problemas", "📷 Revisor de Divisiones"])

# ==========================================
# PESTAÑA 1: PROBLEMAS INTERACTIVOS
# ==========================================
with tab1:
    st.header("Problemas Razonados Interactivos")
    
    col1, col2 = st.columns(2)
    with col1:
        grado = st.selectbox("Selecciona el grado escolar:", ["1° - 2° Primaria", "3° - 4° Primaria", "5° - 6° Primaria"])
    with col2:
        tema = st.text_input("¿Qué le gusta al niño?:", "Minecraft")

    if st.button("🎲 Generar nuevo problema"):
        prompt = (
            f"Escribe un problema matemático para un alumno de {grado} ambientado en el tema '{tema}'. "
            "Formula exactamente 1 problema claro que incluya 2 o 3 preguntas concretas al final para responder con números. "
            "Separa la respuesta en dos secciones marcadas exactamente así:\n"
            "---PROBLEMA---\n"
            "(Aquí escribe el texto del problema y las preguntas)\n"
            "---SOLUCION---\n"
            "(Aquí escribe la solución paso a paso y las respuestas numéricas exactas)"
        )
        
        with st.spinner("Creando problema..."):
            try:
                texto_completo = generar_con_respaldo(prompt)
                
                if "---PROBLEMA---" in texto_completo and "---SOLUCION---" in texto_completo:
                    partes = texto_completo.split("---SOLUCION---")
                    st.session_state['problema_texto'] = partes[0].replace("---PROBLEMA---", "").strip()
                    st.session_state['solucion_texto'] = partes[1].strip()
                else:
                    st.session_state['problema_texto'] = texto_completo
                    st.session_state['solucion_texto'] = "Revisa las preguntas con atención y calcula los resultados."
                
                st.session_state['respuesta_alumno'] = ""
                st.session_state['evaluacion'] = None
            except Exception as e:
                st.error(f"Error al generar: {e}")

    # Mostrar problema si existe en la sesión
    if 'problema_texto' in st.session_state:
        st.markdown("---")
        st.subheader("📋 Problema para resolver:")
        st.info(st.session_state['problema_texto'])
        
        respuesta_usuario = st.text_area(
            "✍️ Escribe aquí tus respuestas a las preguntas:", 
            key="respuesta_alumno",
            height=120,
            placeholder="Ejemplo:\n1) 15 manzanas\n2) 30 pesos"
        )
        
        if st.button("✅ Verificar o revisar respuestas"):
            if not respuesta_usuario.strip():
                st.warning("Escribe tus respuestas antes de revisar.")
            else:
                prompt_eval = (
                    f"El alumno recibió este problema:\n{st.session_state['problema_texto']}\n\n"
                    f"La solución correcta es:\n{st.session_state['solucion_texto']}\n\n"
                    f"El alumno respondió:\n{respuesta_usuario}\n\n"
                    "Eres un maestro de primaria muy amable y alentador. Evalúa la respuesta del alumno. "
                    "Indícale de forma amigable en qué acertó y, si se equivocó, explícale con tacto cómo corregirlo. Usa emojis."
                )
                with st.spinner("Revisando tu respuesta..."):
                    try:
                        evaluacion = generar_con_respaldo(prompt_eval)
                        st.session_state['evaluacion'] = evaluacion
                    except Exception as e:
                        st.error(f"Error al evaluar: {e}")

    if st.session_state.get('evaluacion'):
        st.success("### 🍎 Resultado del Profe:")
        st.write(st.session_state['evaluacion'])

# ==========================================
# PESTAÑA 2: REVISOR DE DIVISIONES
# ==========================================
with tab2:
    st.header("Revisar División de Cuaderno")
    st.write("Sube la foto de la división resuelta en la libreta para verificar el procedimiento escolar paso a paso.")
    
    foto = st.file_uploader("Sube la foto del cuaderno:", type=["jpg", "jpeg", "png"])
    
    if foto is not None:
        imagen = Image.open(foto)
        st.image(imagen, caption="Imagen cargada", width=350)
        
        if st.button("🔍 Revisar procedimiento"):
            prompt_vision = (
                "Eres un maestro especialista en matemáticas de educación primaria. "
                "Analiza la imagen enviada de una división resuelta a mano en un cuaderno de cuadrícula.\n\n"
                "Sigue exactamente la metodología escolar tradicional:\n"
                "1. Identifica el dividendo (número adentro de la casita), el divisor (afuera), el cociente (arriba) y las restas intermedias.\n"
                "2. Revisa paso a paso cada multiplicación y resta en el procedimiento vertical.\n"
                "3. Revisa la posición del punto decimal si aplica.\n"
                "4. Explica detalladamente como un profesor de primaria:\n"
                "   - Indica la operación realizada (ej. 7386.94 entre 38).\n"
                "   - Si está correcta, felicita al estudiante destacando la alineación y el procedimiento ordenado.\n"
                "   - Si hay algún error, señala la cifra exacta o el paso donde ocurrió la resta o bajada de número incorrecta para que el alumno aprenda a corregirlo."
            )
            with st.spinner("Analizando división paso a paso..."):
                try:
                    resultado = generar_con_respaldo([imagen, prompt_vision])
                    st.write(resultado)
                except Exception as e:
                    st.error(f"Error al analizar la imagen: {e}")
