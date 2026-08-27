import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import qrcode
from io import BytesIO

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(
    page_title="AI Readiness & Teacher Role Polling",
    page_icon="🤖",
    layout="wide"
)

# --- ระบบฐานข้อมูล (SQLite ในตัว) ---
def init_db():
    conn = sqlite3.connect("poll_data.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            percentage INTEGER,
            keyword TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_response(percentage, keyword):
    conn = sqlite3.connect("poll_data.db")
    c = conn.cursor()
    c.execute("INSERT INTO responses (percentage, keyword) VALUES (?, ?)", 
              (percentage, keyword.strip()))
    conn.commit()
    conn.close()

def get_data():
    conn = sqlite3.connect("poll_data.db")
    df = pd.read_sql_query("SELECT * FROM responses", conn)
    conn.close()
    return df

def clear_db():
    conn = sqlite3.connect("poll_data.db")
    c = conn.cursor()
    c.execute("DELETE FROM responses")
    conn.commit()
    conn.close()

init_db()

# --- เมนูด้านข้าง (Navigation & Controls) ---
st.sidebar.title("🎛️ Control Panel")
mode = st.sidebar.radio("เลือกหน้าจอแสดงผล:", ["📱 สำหรับนักศึกษา (Vote)", "📊 จอโปรเจกเตอร์วิทยากร (Live Dashboard)"])

# ==========================================
# 1. หน้านักศึกษา (Mobile Voting Interface)
# ==========================================
if mode == "📱 สำหรับนักศึกษา (Vote)":
    st.markdown("### 🎓 กิจกรรมที่ 1: Check-in & AI Readiness")
    st.info("ร่วมสะท้อนมุมมองเพื่อค้นหาอัตลักษณ์ครูยุคใหม่ในยุค AI")

    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    if not st.session_state.submitted:
        with st.form("vote_form"):
            st.markdown("#### 1. ในห้องเรียนอนาคต ท่านคิดว่า AI จะเข้ามาทำงานแทนที่ครูในสัดส่วนกี่เปอร์เซ็นต์?")
            percentage = st.slider(
                "เลื่อนระดับเปอร์เซ็นต์ (0% = ไม่ได้เลย, 100% = ทั้งหมด)", 
                min_value=0, max_value=100, value=50, step=5
            )
            
            st.markdown("---")
            st.markdown("#### 2. เมื่อ AI รู้ทุกคำตอบในโลก... บทบาทอันดับ 1 ของครูจะเปลี่ยนเป็น 'ผู้...?'")
            keyword = st.text_input(
                "พิมพ์คำกริยาหรือบทบาทสั้นๆ 1 คำ (เช่น ผู้จุดประกาย, โค้ช, ผู้รับฟัง)",
                max_chars=25,
                placeholder="ระบุ 1 คำ..."
            )
            
            submit_btn = st.form_submit_button("🚀 ส่งคำตอบ", use_container_width=True)
            
            if submit_btn:
                if keyword.strip() == "":
                    st.error("กรุณาระบุคำตอบข้อที่ 2 ก่อนส่งครับ")
                else:
                    save_response(percentage, keyword)
                    st.session_state.submitted = True
                    st.rerun()
    else:
        st.success("🎉 บันทึกคำตอบเรียบร้อยแล้ว ขอบคุณที่ร่วมกิจกรรมครับ!")
        if st.button("ส่งคำตอบใหม่อีกครั้ง"):
            st.session_state.submitted = False
            st.rerun()

# ==========================================
# 2. หน้าจอโปรเจกเตอร์วิทยากร (Live Dashboard)
# ==========================================
else:
    col_head, col_refresh = st.columns([4, 1])
    with col_head:
        st.markdown("## 📊 ผลลัพธ์สด: มนุษย์ vs AI & อัตลักษณ์ครูยุคใหม่")
    with col_refresh:
        if st.button("🔄 อัปเดตข้อมูลสด", use_container_width=True):
            st.rerun()

    df = get_data()

    if df.empty:
        st.warning("⚠️ ยังไม่มีข้อมูลผู้ตอบแบบสอบถาม กรุณาให้นักศึกษาสแกน QR Code เพื่อส่งคำตอบ")
        
        # กล่องสร้าง QR Code หน้าจอสำหรับวิทยากร
        app_url = st.text_input("ใส่ URL ของเว็บนี้ เพื่อสร้าง QR Code ให้ผู้เรียนสแกน:", "http://localhost:8501")
        qr = qrcode.make(app_url)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="สแกนเพื่อร่วมกิจกรรม", width=250)
    else:
        # สรุปสถิติภาพรวม
        total_votes = len(df)
        avg_pct = df["percentage"].mean()
        median_pct = df["percentage"].median()

        m1, m2, m3 = st.columns(3)
        m1.metric("👥 ผู้เข้าร่วมทั้งหมด", f"{total_votes} คน")
        m2.metric("📈 สัดส่วนเฉลี่ยที่ AI แทนที่ได้", f"{avg_pct:.1f} %")
        m3.metric("🎯 ค่ามัธยฐาน (Median)", f"{median_pct:.0f} %")

        st.markdown("---")
        
        # จัด Layout กราฟซ้าย-ขวา
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("#### 📉 การกระจายตัวของมุมมอง (0 - 100%)")
            fig_hist = px.histogram(
                df, x="percentage", nbins=10, 
                labels={"percentage": "สัดส่วนที่ AI แทนที่ครู (%)"},
                color_discrete_sequence=["#1E88E5"],
                range_x=[0, 100]
            )
            fig_hist.add_vline(x=avg_pct, line_dash="dash", line_color="red", 
                               annotation_text=f"Mean: {avg_pct:.1f}%")
            fig_hist.update_layout(bargap=0.1, yaxis_title="จำนวนผู้ตอบ (คน)")
            st.plotly_chart(fig_hist, use_container_width=True)

        with col_right:
            st.markdown("#### ☁️ Smart Word Cloud: บทบาทครูที่ AI แทนไม่ได้")
            text_corpus = " ".join(df["keyword"].dropna().tolist())
            
            if text_corpus.strip():
                try:
                    # สร้าง Word Cloud
                    wc = WordCloud(
                        width=600, height=400, 
                        background_color="white",
                        colormap="viridis",
                        regexp=r"\w+"
                    ).generate(text_corpus)
                    
                    fig_wc, ax = plt.subplots(figsize=(6, 4))
                    ax.imshow(wc, interpolation="bilinear")
                    ax.axis("off")
                    st.pyplot(fig_wc)
                except Exception:
                    # แผนสำรองถ้าไม่มี font ภาษาไทย: แสดง Top Ranking Bar Chart
                    top_words = df["keyword"].value_counts().reset_index()
                    top_words.columns = ["บทบาท", "จำนวน"]
                    fig_bar = px.bar(top_words.head(8), x="จำนวน", y="บทบาท", orientation="h", color="จำนวน")
                    st.plotly_chart(fig_bar, use_container_width=True)

        # จัดการข้อมูลด้านล่าง
        with st.expander("⚙️ เครื่องมือจัดการข้อมูล (สำหรับวิทยากร)"):
            st.dataframe(df.tail(10))
            if st.button("🗑️ ล้างข้อมูลทั้งหมดเพื่อเริ่มรอบใหม่", type="primary"):
                clear_db()
                st.rerun()