import streamlit as st
from ui_hakem_paneli import hakem_panelini_ciz

# Mobil uyumlu geniş ekran ayarı
st.set_page_config(
    page_title="Başhakem Asistanı", 
    page_icon="🎾", 
    layout="centered"
)

def main():
    hakem_panelini_ciz()

if __name__ == "__main__":
    main()
