import streamlit as st
import base64
from openai import OpenAI
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# Configuración inicial
st.set_page_config(page_title='Corrector Matemático')
st.title('Corrector Matemático')

# Configuración de barra lateral
with st.sidebar:
    st.subheader("Configuración")
    api_key = st.text_input('Ingresa tu API Key de OpenAI', type="password")
    st.markdown("---")
    st.subheader("Herramientas de dibujo")
    stroke_width = st.slider('Grosor del trazo', 1, 30, 5)
    stroke_color = st.color_picker("Color del trazo", "#000000")

# Lienzo interactivo
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 1)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color="#FFFFFF",
    height=400,
    width=600,
    drawing_mode="freedraw",
    key="canvas",
)

analyze_button = st.button("Resolver Operación", type="primary")

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Lógica de ejecución
if analyze_button:
    if not api_key:
        st.error("Error: Se requiere la API Key de OpenAI para ejecutar el análisis.")
        st.stop()
        
    if canvas_result.image_data is not None:
        with st.spinner("Procesando la operación matemática..."):
            
            # Captura y guardado temporal de la imagen
            input_numpy_array = np.array(canvas_result.image_data)
            input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
            input_image.save('img_math.png')
            base64_image = encode_image_to_base64("img_math.png")

            # Directiva estricta para el modelo
            prompt_text = (
                "Eres un corrector matemático estricto. Analiza la imagen. "
                "Si identificas claramente una operación matemática, resuélvela y responde ÚNICAMENTE con el formato: 'Esta es la respuesta: [resultado final]'. "
                "Si la imagen está vacía, contiene dibujos sin sentido, texto no matemático o la operación es incomprensible, responde ÚNICAMENTE con la frase: 'Vuelve a escribir'."
            )

            client = OpenAI(api_key=api_key)

            try:
                # Petición a la API
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}",
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=100,
                )
                
                # Despliegue del resultado
                resultado = response.choices[0].message.content.strip()
                st.subheader("Resultado:")
                st.write(resultado)

            except Exception as e:
                st.error(f"Excepción capturada durante la solicitud a la API: {e}")
    else:
        st.warning("El tablero no contiene datos para analizar.")
