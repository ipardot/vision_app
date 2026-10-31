import os
import streamlit as st
import base64
from openai import OpenAI

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")


st.set_page_config(page_title="Chef de Nevera", page_icon="🥕", layout="centered", initial_sidebar_state="collapsed")

# ------------------------------------------------------------------
# TEMA "CHEF DE NEVERA" (solo estilos CSS; la lógica y los inputs no cambian)
# ------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,800&family=Nunito:wght@400;600;700&display=swap');

:root{
  --pared:#f6f0e6;
  --salvia:#5e7d57;
  --salvia-oscuro:#3f5a3b;
  --salvia-claro:#dfe8d6;
  --roble:#c99a66;
  --roble-oscuro:#9c6f43;
  --naranja:#e2763a;
  --tinta:#2f3a2c;
}

/* Fondo: pared crema con el mesón de madera abajo */
.stApp{
  background:
    linear-gradient(to bottom,
      transparent calc(100% - 70px),
      #efe4d2 calc(100% - 70px),
      #efe4d2 calc(100% - 62px),
      var(--roble) calc(100% - 62px)),
    var(--pared);
  background-attachment: fixed;
}
header[data-testid="stHeader"]{ background: transparent; }

/* Panel central: ficha de receta */
[data-testid="stMainBlockContainer"], .block-container{
  background:#fffdf9;
  border-radius:22px;
  border-top:10px solid var(--salvia);
  box-shadow:0 18px 40px rgba(94,74,40,.14);
  margin-top:2rem;
  margin-bottom:6rem;
  padding:2rem 2.4rem 2.4rem !important;
  max-width:780px;
}
@media (max-width:640px){
  [data-testid="stMainBlockContainer"], .block-container{
    padding:1.4rem 1.1rem 1.8rem !important;
    border-radius:16px;
  }
}

/* Encabezado */
.chef-tag{
  display:inline-block;
  font-family:'Nunito', sans-serif;
  font-weight:700; font-size:.8rem; letter-spacing:.12em; text-transform:uppercase;
  color:var(--salvia-oscuro);
  background:var(--salvia-claro);
  padding:.3rem .8rem; border-radius:999px;
}
.chef-title{
  font-family:'Fraunces', serif;
  font-weight:800; font-size:2.7rem; line-height:1.05;
  color:var(--salvia-oscuro);
  margin:.7rem 0 .6rem;
}
.chef-title span{ color:var(--naranja); }
.chef-sub{
  font-family:'Nunito', sans-serif;
  font-size:1.08rem; line-height:1.55;
  color:#5b5246;
}
@media (max-width:640px){
  .chef-title{ font-size:2rem; }
}

/* Foto del encabezado */
[data-testid="stImage"] img{
  border-radius:18px;
  box-shadow:0 10px 24px rgba(63,90,59,.22);
}

/* Separador tipo repisa de madera */
.chef-repisa{
  height:10px; border-radius:6px;
  background:linear-gradient(var(--roble), var(--roble-oscuro));
  margin:1.6rem 0 1.4rem;
}

/* Textos de la respuesta (recetario) */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li{
  font-family:'Nunito', sans-serif;
  color:var(--tinta);
  line-height:1.6;
}
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3{
  font-family:'Fraunces', serif !important;
  color:var(--salvia-oscuro) !important;
}
[data-testid="stMarkdownContainer"] strong{ color:var(--roble-oscuro); }
h1 a, h2 a, h3 a{ display:none !important; }
/* Botones y avisos: conservan los colores originales de Streamlit (contraste) */
button [data-testid="stMarkdownContainer"],
button [data-testid="stMarkdownContainer"] *,
[data-testid="stAlert"] [data-testid="stMarkdownContainer"] *{
  color:inherit !important;
  font-family:inherit !important;
}
</style>
""", unsafe_allow_html=True)

# Título tipo recetario
st.markdown("""
<span class="chef-tag">🥕 Tu cocina, con IA</span>
<div class="chef-title">Chef de <span>Nevera</span></div>
<div class="chef-sub">Abre la nevera, toma una foto y mira la lista de alimentos de lo que ya tienes, para facilitar las compras en el super.</div>
""", unsafe_allow_html=True)

# Imagen de portada
try:
    st.image('nevera.webp', width=350)
except Exception as e:
    st.warning(f"No se pudo cargar la imagen: {e}")

st.markdown('<div class="chef-repisa"></div>', unsafe_allow_html=True)

ke = st.text_input('🔑 Ingresa tu clave de OpenAI')
os.environ['OPENAI_API_KEY'] = ke


# Retrieve the OpenAI API Key from secrets
api_key = os.environ['OPENAI_API_KEY']

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

# File uploader allows user to add their own image
uploaded_file = st.file_uploader("📸 Sube una foto de tu nevera o tus ingredientes", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Display the uploaded image
    with st.expander("🧊 Tu nevera", expanded = True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# Toggle for showing additional details input
show_details = st.toggle("🍳 Tengo una preferencia (vegetariano, rápido, postre…)", value=False)

if show_details:
    # Text input for additional details about the image, shown only if toggle is True
    additional_details = st.text_area(
        "Cuéntale al chef qué se te antoja o qué quieres saber:",
        disabled=not show_details
    )

# Button to trigger the analysis
analyze_button = st.button("👩‍🍳 ¿Qué cocino hoy?", type="secondary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if uploaded_file is not None and api_key and analyze_button:

    with st.spinner("El chef está revisando tu nevera..."):
        # Encode the image
        base64_image = encode_image(uploaded_file)
    
        prompt_text = ("Describe what you see in the image in spanish")
    
        if show_details and additional_details:
            prompt_text += (
                f"\n\nAdditional Context Provided by the User:\n{additional_details}"
            )
    
        # Create the payload for the completion request - CORRECTED FORMAT
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                ],
            }
        ]
    
        # Make the request to the OpenAI API
        try:
            # Stream the response
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4o", messages=messages,   
                max_tokens=1200, stream=True
            ):
                # Check if there is content to display
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)
    
        except Exception as e:
            st.error(f"Ups, algo se quemó en la cocina: {e}")
else:
    # Warnings for user action required
    if not uploaded_file and analyze_button:
        st.warning("Primero sube una foto de tu nevera o tus ingredientes.")
    if not api_key:
        st.warning("Ingresa tu clave de OpenAI para empezar a cocinar.")
