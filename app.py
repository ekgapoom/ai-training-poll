import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import qrcode
from io import BytesIO
import textwrap

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(
    page_title="กิจกรรมที่ 1: Check-in & AI Readiness (100 Users)",
    page_icon="🤖",
    layout="wide"
)

# --- 2. ปรับแต่ง CSS ล็อกสีตัวอักษรเพื่อความคมชัดทุกธีม ---
custom_css = textwrap.dedent("""
<style>
    .main-header {
        font-size: 24px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size: 15px;
        color: #4B5563;
        margin-bottom: 20px;
    }
    .poll-card {
        background-color: #FFFFFF !important;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #E2E8F0;
        border-top: 4px solid #3B82F6;
        color: #1E293B !important;
    }
    .badge-user {
        background-color: #EFF6FF !important;
        color: #1D4ED8 !important;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 12.5px;
        font-weight: 600;
    }
    .badge-percent {
        background-color: #FEF3C7 !important;
        color: #92400E !important;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: bold;
    }
</style>
""")
st.markdown(custom_css, unsafe_allow_html=True)

# --- 3. ระบบฐานข้อมูล SQLite รองรับ 100+ ผู้ใช้พร้อมกัน ---
DB_NAME = "poll_activity1_100users.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=30.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")  # ป้องกัน DB Lock เมื่อ 100 คนส่งพร้อมกัน
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT,
                student_id TEXT,
                percentage INTEGER,
                keyword TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def save_response(student_name, student_id, percentage, keyword):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO responses (student_name, student_id, percentage, keyword) 
            VALUES (?, ?, ?, ?)
        """, (student_name.strip(), student_id.strip(), percentage, keyword.strip()))
        conn.commit()

def get_data():
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM responses ORDER BY id DESC", conn)
    return df

def clear_db():
    with get_connection() as conn:
        conn.execute("DELETE FROM responses")
        conn.commit()

init_db()

# --- 4. เมนูด้านข้าง (Sidebar) ---
st.sidebar.title("🤖 Activity 1 Control")
mode = st.sidebar.radio(
    "เลือกมุมมองหน้าจอ:",
    ["📱 สำหรับนักศึกษา (ร่วมตอบคำถาม)", "📊 จอโปรเจกเตอร์วิทยากร (Live Dashboard)"]
)

# ==============================================================================
# 5. หน้านักศึกษา (Mobile Voting Interface)
# ==============================================================================
if mode == "📱 สำหรับนักศึกษา (ร่วมตอบคำถาม)":
    header_html = textwrap.dedent("""
    <div class='main-header'>🎓 กิจกรรมที่ 1: Check-in & AI Readiness</div>
    <div class='sub-header'>ร่วมสะท้อนมุมมองเพื่อค้นหาจุดยืนและอัตลักษณ์ครูยุคใหม่ในยุค AI</div>
    """)
    st.markdown(header_html, unsafe_allow_html=True)

    if "submitted_act1" not in st.session_state:
        st.session_state.submitted_act1 = False

    if not st.session_state.submitted_act1:
        with st.form("vote_form"):
            st.markdown("#### 👤 ข้อมูลผู้ร่วมกิจกรรม")
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                student_name = st.text_input("ชื่อ - นามสกุล:", placeholder="เช่น นายสมชาย ใจดี")
            with col_u2:
                student_id = st.text_input("รหัสนักศึกษา / สาขาวิชา:", placeholder="เช่น 66123456 เอกวิทยาศาสตร์")

            st.markdown("---")
            st.markdown("#### 1️⃣ ในห้องเรียนอนาคต ท่านคิดว่า AI จะเข้ามาทำงานแทนที่ครูในสัดส่วนกี่เปอร์เซ็นต์?")
            percentage = st.slider(
                "เลื่อนระดับเปอร์เซ็นต์ (0% = ไม่ได้เลย, 100% = ทั้งหมด)", 
                min_value=0, max_value=100, value=50, step=5
            )
            
            st.markdown("---")
            st.markdown("#### 2️⃣ เมื่อ AI รู้ทุกคำตอบในโลก... บทบาทอันดับ 1 ของครูจะเปลี่ยนเป็น 'ผู้...?'")
            keyword = st.text_input(
                "พิมพ์คำกริยาหรือบทบาทสั้นๆ 1 คำ (เช่น ผู้จุดประกาย, โค้ช, ผู้รับฟัง, ผู้อำนวยการเรียนรู้)",
                max_chars=30,
                placeholder="ระบุ 1 คำ..."
            )
            
            submit_btn = st.form_submit_button("🚀 ส่งคำตอบของฉัน", use_container_width=True)
            
            if submit_btn:
                if not student_name or not student_id or not keyword.strip():
                    st.error("⚠️ กรุณากรอกข้อมูลให้ครบถ้วนทุกช่องก่อนกดส่งครับ")
                else:
                    save_response(student_name, student_id, percentage, keyword)
                    st.session_state.submitted_act1 = True
                    st.rerun()
    else:
        st.success("🎉 บันทึกคำตอบของคุณเรียบร้อยแล้ว ขอบคุณที่ร่วมแบ่งปันมุมมองครับ!")
        if st.button("➕ ส่งคำตอบใหม่ / แก้ไข"):
            st.session_state.submitted_act1 = False
            st.rerun()

# ==============================================================================
# 6. หน้าจอโปรเจกเตอร์วิทยากร / Canva Embed (Live Dashboard 100 คน)
# ==============================================================================
else:
    col_head, col_refresh = st.columns([3, 1])
    with col_head:
        dash_header = textwrap.dedent("""
        <div class='main-header'>📊 ผลลัพธ์สด: มนุษย์ vs AI & อัตลักษณ์ครูยุคใหม่</div>
        <div class='sub-header'>วิเคราะห์มุมมองและทัศนคติของว่าที่ครูทั้งห้องประชุม</div>
        """)
        st.markdown(dash_header, unsafe_allow_html=True)
    with col_refresh:
        if st.button("🔄 อัปเดตข้อมูลสด", use_container_width=True):
            st.rerun()

    df = get_data()

    if df.empty:
        st.warning("⏳ ยังไม่มีผู้ส่งคำตอบ กรุณาให้นักศึกษาสแกน QR Code ด้านล่างเพื่อเริ่มกิจกรรม")
        app_url = st.text_input("ใส่ URL ของเว็บนี้ เพื่อสร้าง QR Code ให้ผู้เรียนสแกน:", "http://localhost:8501")
        qr = qrcode.make(app_url)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="สแกนเพื่อร่วมกิจกรรมที่ 1", width=220)
    else:
        # สรุปสถิติภาพรวมของผู้เข้าอบรมทั้งหมด
        total_votes = len(df)
        avg_pct = df["percentage"].mean()
        median_pct = df["percentage"].median()

        m1, m2, m3 = st.columns(3)
        m1.metric("👥 ผู้เข้าร่วมทั้งหมด", f"{total_votes} คน")
        m2.metric("📈 สัดส่วนเฉลี่ยที่ AI แทนที่ได้", f"{avg_pct:.1f} %")
        m3.metric("🎯 ค่ามัธยฐาน (Median)", f"{median_pct:.0f} %")

        st.markdown("---")
        
        # จัด Layout แสดงกราฟคู่ (ซ้าย: Histogram การกระจายตัว, ขวา: Smart Word Cloud / Top Roles)
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("#### 📉 การกระจายตัวของมุมมอง (0 - 100%)")
            fig_hist = px.histogram(
                df, x="percentage", nbins=10, 
                labels={"percentage": "สัดส่วนที่ AI แทนที่ครู (%)"},
                color_discrete_sequence=["#2563EB"],
                range_x=[0, 100]
            )
            fig_hist.add_vline(x=avg_pct, line_dash="dash", line_color="#DC2626", 
                               annotation_text=f"Mean: {avg_pct:.1f}%")
            fig_hist.update_layout(bargap=0.1, yaxis_title="จำนวนผู้ตอบ (คน)", height=320, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_hist, use_container_width=True)

        with col_right:
            st.markdown("#### ☁️ บทบาทครูที่ AI แทนไม่ได้ (Top Keywords)")
            text_corpus = " ".join(df["keyword"].dropna().tolist())
            
            # ดึงคำยอดนิยมแสดงผลเป็น Bar Chart ควบคู่
            top_words = df["keyword"].value_counts().reset_index()
            top_words.columns = ["บทบาท", "จำนวนคนตอบ"]
            
            fig_bar = px.bar(
                top_words.head(8), 
                x="จำนวนคนตอบ", 
                y="บทบาท", 
                orientation="h", 
                color="จำนวนคนตอบ",
                color_continuous_scale="Blues"
            )
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=320, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        
        # รายการคำตอบรายบุคคลพร้อมระบบค้นหาและแบ่งหน้า
        st.markdown("### 💬 เจาะลึกมุมมองรายบุคคล")
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            search_query = st.text_input("🔍 ค้นหาชื่อ / รหัส / บทบาท:", placeholder="พิมพ์ค้นหา...")
        with col_s2:
            items_per_page = st.selectbox("แสดงผลหน้าละ:", [10, 20, 50, 100], index=0)

        filtered_df = df
        if search_query.strip():
            filtered_df = df[
                df["student_name"].str.contains(search_query, case=False, na=False) |
                df["student_id"].str.contains(search_query, case=False, na=False) |
                df["keyword"].str.contains(search_query, case=False, na=False)
            ]

        st.caption(f"แสดง {min(items_per_page, len(filtered_df))} จากทั้งหมด {len(filtered_df)} คน")

        cols = st.columns(2)
        for idx, row in filtered_df.head(items_per_page).reset_index().iterrows():
            col_target = cols[idx % 2]
            with col_target:
                card_html = textwrap.dedent(f"""
                <div class='poll-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>
                        <span style='font-size: 15px; font-weight: bold; color: #1E3A8A;'>👤 {row['student_name']}</span>
                        <span class='badge-user'>{row['student_id']}</span>
                    </div>
                    <div style='margin-top: 6px; font-size: 14px;'>
                        📊 สัดส่วน AI แทนที่: <span class='badge-percent'>{row['percentage']}%</span>
                    </div>
                    <div style='margin-top: 8px; font-size: 14px;'>
                        🎯 บทบาทอันดับ 1 ของครู: <b style='color: #2563EB;'>"{row['keyword']}"</b>
                    </div>
                </div>
                """)
                st.markdown(card_html, unsafe_allow_html=True)

        # เมนูสำหรับวิทยากรดาวน์โหลด
        st.markdown("---")
        with st.expander("⚙️ เครื่องมือจัดการข้อมูลและส่งออกคะแนน (สำหรับวิทยากร)"):
            st.dataframe(df)
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลดผลโหวต 100 คนเป็น Excel/CSV",
                data=csv_data,
                file_name="activity1_poll_results.csv",
                mime="text/csv"
            )
            if st.button("🗑️ ล้างข้อมูลทั้งหมดเพื่อเริ่มรอบใหม่", type="primary"):
                clear_db()
                st.rerun()
