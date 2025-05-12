import streamlit as st
from graph_build import app as graph  
from log_feedback import log_to_mongo, get_logs_from_mongo


import os
st.write("Uygulama dizinindeki dosyalar:", os.listdir())

initialize_log()

st.set_page_config(page_title="Goldberg Sterilizatör Yardımcısı", layout="centered")
st.markdown("<h1 style='text-align: center;'>GoldbergMed H₂O₂ Sterilizatör Asistanı</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; font-size: 18px;'>"
    "Hidrojen peroksit bazlı sterilizatör kullanımıyla ilgili sorularınıza anında cevap alın."
    "</p>",
    unsafe_allow_html=True
)



user_query = st.text_input("Sormak istediğiniz soruyu giriniz:")

if user_query:
    with st.spinner("Yanıt hazırlanıyor..."):
        result = graph.invoke({"input": user_query})
        cevap = result["output"]
        ajan = result["agent_type"]

    st.markdown("### 🗨️ Yanıt")
    st.success(cevap)

    st.markdown(f"**🧠 Kullanılan Ajan:** `{ajan}`")

    st.markdown("---")
    st.markdown("### 🙋 Geri Bildiriminiz")

    col1, col2 = st.columns([1, 3])
    with col1:
        feedback = st.radio("Yararlı mıydı?", ["👍", "👎"], horizontal=True)
    with col2:
        yorum = st.text_input("Yorumunuz (isteğe bağlı)")

    if st.button("Gönder"):
        log_interaction(user_query, ajan, cevap, feedback, yorum)
        st.success("Teşekkür ederiz, geri bildiriminiz kaydedildi.")

# ... yanıt ve geri bildirim işlemleri burada olur

if st.sidebar.checkbox("🧾 MongoDB Loglarını Gör"):
    logs = get_logs_from_mongo()
    if logs:
        df = pd.DataFrame(logs)
        st.dataframe(df[["timestamp", "soru", "ajan", "geri_bildirim", "yorum"]])
    else:
        st.info("Kayıt bulunamadı.")
