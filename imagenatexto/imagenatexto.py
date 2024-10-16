import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator

# Ruta de la carpeta donde están las imágenes y demás archivos
BASE_DIR = "imagenatexto"
IMAGE_FOLDER = os.path.join(BASE_DIR, "imagen a texto")
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Configurar la ruta de Tesseract si estás en Windows
# En Linux/Mac no necesitas esto si Tesseract está en el PATH
pytesseract.pytesseract.tesseract_cmd = os.path.join(BASE_DIR, 'Tesseract-OCR', 'tesseract.exe')

text = " "

def text_to_speech(input_language, output_language, text, tld):
    # Asegurarse de que el texto no esté vacío
    if not text.strip():
        st.error("El texto está vacío. No hay nada que convertir a audio.")
        return None, None

    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    
    try:
        my_file_name = text[0:20]  # Nombre del archivo basado en el texto
    except:
        my_file_name = "audio"
    
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, trans_text

def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)
                print("Deleted ", f)

remove_files(7)

st.title("Reconocimiento Óptico de Caracteres (OCR)")

# Mostrar imagen fija de ejemplo desde la carpeta "imagenatexto"
image_path = os.path.join(BASE_DIR, "image_2024-10-15_110057995.png")
if os.path.exists(image_path):
    image = Image.open(image_path)
    st.image(image, caption="Afterlifes")
else:
    st.error(f"No se encontró la imagen: {image_path}")

st.subheader("Elige la fuente de la imagen, esta puede venir de la cámara o cargando un archivo")

cam_ = st.checkbox("Usar Cámara")

if cam_:
    img_file_buffer = st.camera_input("Toma una Foto")
else:
    img_file_buffer = None

with st.sidebar:
    st.subheader("Procesamiento para Cámara")
    filtro = st.radio("Filtro para imagen con cámara", ('Sí', 'No'))

# Cargar imágenes desde la carpeta
bg_image = st.file_uploader("Cargar Imagen desde 'imagen a texto':", type=["png", "jpg"])
if bg_image is not None:
    # Guardar la imagen en la carpeta "imagen a texto"
    file_path = os.path.join(IMAGE_FOLDER, bg_image.name)
    with open(file_path, 'wb') as f:
        f.write(bg_image.read())
    
    st.success(f"Imagen guardada en {file_path}")
    img_cv = cv2.imread(file_path)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    
    # Verificar si el OCR produjo texto
    if text.strip():
        st.write(text)
    else:
        st.error("No se pudo extraer texto de la imagen. Verifique la calidad de la imagen o cargue otra.")

if img_file_buffer is not None:
    # Procesar la imagen tomada por la cámara
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    if filtro == 'Sí':
        cv2_img = cv2.bitwise_not(cv2_img)

    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

    # Verificar si el OCR produjo texto
    if text.strip():
        st.write(text)
    else:
        st.error("No se pudo extraer texto de la imagen tomada por la cámara.")

# Sección de traducción y conversión a audio
with st.sidebar:
    st.subheader("Parámetros de traducción")
    
    try:
        os.mkdir("temp")
    except:
        pass
    
    translator = Translator()

    in_lang = st.selectbox(
        "Seleccione el lenguaje de entrada",
        ("Ingles", "Español", "Bengali", "koreano", "Mandarin", "Japones"),
    )

    if in_lang == "Ingles":
        input_language = "en"
    elif in_lang == "Español":
        input_language = "es"
    elif in_lang == "Bengali":
        input_language = "bn"
    elif in_lang == "koreano":
        input_language = "ko"
    elif in_lang == "Mandarin":
        input_language = "zh-cn"
    elif in_lang == "Japones":
        input_language = "ja"

    out_lang = st.selectbox(
        "Seleccione el lenguaje de salida",
        ("Ingles", "Español", "Bengali", "koreano", "Mandarin", "Japones"),
    )

    if out_lang == "Ingles":
        output_language = "en"
    elif out_lang == "Español":
        output_language = "es"
    elif out_lang == "Bengali":
        output_language = "bn"
    elif out_lang == "koreano":
        output_language = "ko"
    elif out_lang == "Mandarin":
        output_language = "zh-cn"
    elif out_lang == "Japones":
        output_language = "ja"

    english_accent = st.selectbox(
        "Seleccione el acento",
        ("Default", "India", "United Kingdom", "United States", "Canada", "Australia", "Ireland", "South Africa"),
    )

    if english_accent == "Default":
        tld = "com"
    elif english_accent == "India":
        tld = "co.in"
    elif english_accent == "United Kingdom":
        tld = "co.uk"
    elif english_accent == "United States":
        tld = "com"
    elif english_accent == "Canada":
        tld = "ca"
    elif english_accent == "Australia":
        tld = "com.au"
    elif english_accent == "Ireland":
        tld = "ie"
    elif english_accent == "South Africa":
        tld = "co.za"

    display_output_text = st.checkbox("Mostrar texto")

    if st.button("Convertir"):
        if text.strip():  # Verificar que el texto no esté vacío antes de convertir
            result, output_text = text_to_speech(input_language, output_language, text, tld)
            if result and output_text:
                audio_file = open(f"temp/{result}.mp3", "rb")
                audio_bytes = audio_file.read()
                st.markdown(f"## Tu audio:")
                st.audio(audio_bytes, format="audio/mp3", start_time=0)

                if display_output_text:
                    st.markdown(f"## Texto de salida:")
                    st.write(f" {output_text}")
        else:
            st.error("El texto está vacío, no hay nada que convertir.")
