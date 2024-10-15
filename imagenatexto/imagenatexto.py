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

# Comentar esta línea si estás en Linux o macOS
# En Windows, asegúrate de que la ruta sea correcta
# pytesseract.pytesseract.tesseract_cmd = os.path.join(BASE_DIR, 'Tesseract-OCR', 'tesseract.exe')

text = " "

def text_to_speech(input_language, output_language, text, tld):
    if not text.strip():
        st.error("El texto está vacío. No hay nada que convertir a audio.")
        return None, None

    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)

    try:
        my_file_name = text[0:20]
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

bg_image = st.file_uploader("Cargar Imagen desde 'imagen a texto':", type=["png", "jpg"])
if bg_image is not None:
    file_path = os.path.join(IMAGE_FOLDER, bg_image.name)
    with open(file_path, 'wb') as f:
        f.write(bg_image.read())
    
    st.success(f"Imagen guardada en {file_path}")
    img_cv = cv2.imread(file_path)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    
    if text.strip():
        st.write(text)
    else:
        st.error("No se pudo extraer texto de la imagen. Verifique la calidad de la imagen o cargue otra.")

if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    if filtro == 'Sí':
        cv2_img = cv2.bitwise_not(cv2_img)

    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

    if text.strip():
        st.write(text)
    else:
        st.error("No se pudo extraer texto de la imagen tomada por la cámara.")
