import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# PENGATURAN API KEY (PENTING! GUNAKAN st.secrets UNTUK KEAMANAN)
# ==============================================================================

# Ambil API Key dari Streamlit Secrets
# Pastikan Anda telah menambahkan "GEMINI_API_KEY = 'YOUR_API_KEY'" di file .streamlit/secrets.toml
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("API Key Gemini tidak ditemukan! Harap tambahkan 'GEMINI_API_KEY' di file 'secrets.toml'.")
    st.stop() # Hentikan aplikasi jika API Key tidak ada

# ==============================================================================
# KONFIGURASI MODEL DAN SESI CHAT
# ==============================================================================

# Nama model Gemini
MODEL_NAME = 'gemini-1.5-flash'

# Konteks awal chatbot sebagai apoteker
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Kamu adalah ahli apoteker. Tuliskan obat apa yang diinginkan untuk menyembuhkan penyakit anda. Jawaban singkat dan jelas. Tolak pertanyaan selain tentang obat."]
    },
    {
        "role": "model",
        "parts": ["Baik! Saya akan menjawab pertanyaan Anda tentang obat."]
    }
]

# Inisialisasi Gemini API
genai.configure(api_key=API_KEY)

# ==============================================================================
# FUNGIONALITAS APLIKASI STREAMLIT
# ==============================================================================

# Judul dan deskripsi aplikasi
st.title("👨‍⚕️ Chatbot Apoteker Gemini")
st.write("Tanyakan tentang obat untuk penyakit Anda. Saya akan memberikan jawaban singkat dan jelas. Pertanyaan di luar topik akan saya tolak.")

# Inisialisasi riwayat chat di Streamlit session state jika belum ada
if "chat_history" not in st.session_state:
    st.session_state.chat_history = INITIAL_CHATBOT_CONTEXT
    st.session_state.chat = genai.GenerativeModel(MODEL_NAME).start_chat(
        history=st.session_state.chat_history
    )
    # Tampilkan pesan sambutan dari chatbot
    st.chat_message("assistant").write(st.session_state.chat_history[1]["parts"][0])
else:
    # Tampilkan riwayat chat yang sudah ada
    for message in st.session_state.chat_history:
        role = "assistant" if message["role"] == "model" else "user"
        st.chat_message(role).write(message["parts"][0])

# Input pengguna
if prompt := st.chat_input("Tuliskan penyakit atau gejala Anda..."):
    # Tampilkan input pengguna
    st.chat_message("user").write(prompt)
    st.session_state.chat_history.append({"role": "user", "parts": [prompt]})

    # Kirim prompt ke model dan dapatkan respons
    try:
        response = st.session_state.chat.send_message(prompt, request_options={"timeout": 60})
        
        # Tambahkan respons model ke riwayat chat
        st.session_state.chat_history.append({"role": "model", "parts": [response.text]})

        # Tampilkan respons model
        st.chat_message("assistant").write(response.text)
    except Exception as e:
        st.error(f"Maaf, terjadi kesalahan saat berkomunikasi dengan Gemini: {e}")
