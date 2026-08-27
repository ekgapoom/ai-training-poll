import streamlit as st
import sqlite3
import pandas as pd
import qrcode
from io import BytesIO

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(
    page_title="กิจกรรมที่ 4: Multi-AI Prototyping (งานเดี่ยว)",
    page_icon="🎨",
    layout="wide"
)

# --- 2. ปรับแต่ง CSS ล็อกสีตัวอักษรให้อ่านง่าย คมชัดทุกโหมด ---
custom_css = """
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
.blueprint-card {
    background-color: #FFFFFF !important;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border: 1px solid #E2E8F0;
    border-top: 5px solid #0EA5E9;
    color: #1E293B !important;
}
.badge-user {
    background-color: #EEF2FF !important;
    color: #3730A3 !important;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
}
.badge-grade {
    background-color: #F0FDF4 !important;
    color: #166534 !important;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
}
.section-box {
    background-color: #F8FAFC !important;
    border-left: 3px solid #64748B;
    padding: 8px 12px;
    margin: 6px 0;
    border-radius: 0 6px 6px 0;
    font-size: 13.5px;
    color: #1E293B !important;
}
.blueprint-box {
    background-color: #F0F9FF !important;
    border: 1px dashed #0284C7;
    padding: 12px;
    border-radius: 8px;
    font-size: 13.5px;
    color: #0C4A6E !important;
    margin-top: 8px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- 3. ระบบฐานข้อมูล SQLite (รองรับ 100+ คนพร้อมกัน) ---
DB_NAME = "prototyping_act4_individual.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=30.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS blueprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT,
                student_id TEXT,
                innovation_title TEXT,
                target_grade TEXT,
                text_ai_content TEXT,
                image_ai_content TEXT,
                fact_check_content TEXT,
                blueprint_summary TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def save_blueprint(student_name, student_id, innovation_title, target_grade, text_ai, image_ai, fact_check, blueprint):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO blueprints (
                student_name, student_id, innovation_title, target_grade,
                text_ai_content, image_ai_content, fact_check_content, blueprint_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_name.strip(), student_id.strip(), innovation_title.strip(), target_grade.strip(),
            text_ai.strip(), image_ai.strip(), fact_check.strip(), blueprint.strip()
        ))
        conn.commit()

def get_all_blueprints():
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM blueprints ORDER BY id DESC", conn)
    return df

def clear_db():
    with get_connection() as conn:
        conn.execute("DELETE FROM blueprints")
        conn.commit()

init_db()

# --- 4. เมนูด้านข้าง ---
st.sidebar.title("🎨 Activity 4 Control")
view_mode = st.sidebar.radio(
    "เลือกมุมมองหน้าจอ:",
    ["📱 สำหรับนักศึกษา (ส่งผลงานนวัตกรรม)", "📊 จอโปรเจกเตอร์วิทยากร (Live Showcase)"]
)

# ==============================================================================
# 5. หน้านักศึกษา (Individual Submission)
# ==============================================================================
if view_mode == "📱 สำหรับนักศึกษา (ส่งผลงานนวัตกรรม)":
    st.markdown("<div class='main-header'>🎨 กิจกรรมที่ 4: Multi-AI Prototyping (งานเดี่ยว)</div><div class='sub-header'>โจทย์ Construct & Curate: ผสานเครื่องมือ AI สร้างต้นแบบนวัตกรรมการสอน 1 ชิ้น</div>", unsafe_allow_html=True)

    with st.expander("💡 ทบทวนขั้นตอนการใช้ชุดเครื่องมือ AI", expanded=False):
        st.markdown("""
        * **1. Text AI:** ใช้สร้างสคริปต์คำถามกระตุ้นคิด (Higher-Order Questions) หรือเกณฑ์รูบริกประเมินผล
        * **2. Image AI:** ใช้สร้างภาพประกอบ สื่อการสอน หรือใบงานที่ไม่ติดลิขสิทธิ์
        * **3. Fact-checking:** ตรวจสอบความถูกต้องทางวิชาการและคัดกรองอคติก่อนนำไปใช้
        """)

    if "submitted_act4_ind" not in st.session_state:
        st.session_state.submitted_act4_ind = False

    if not st.session_state.submitted_act4_ind:
        with st.form("prototype_form"):
            st.markdown("#### 👤 ข้อมูลผู้ส่งผลงาน")
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                student_name = st.text_input("ชื่อ - นามสกุล:", placeholder="เช่น นายสมชาย ใจดี")
            with col_u2:
                student_id = st.text_input("รหัสนักศึกษา / สาขาวิชา:", placeholder="เช่น 66123456 เอกวิทยาศาสตร์")

            st.markdown("---")
            st.markdown("#### 🎯 ข้อมูลต้นแบบนวัตกรรมการสอน")
            col_t1, col_t2 = st.columns([2, 1])
            with col_t1:
                innovation_title = st.text_input("ชื่อนวัตกรรม / หัวข้อบทเรียน:", placeholder="เช่น ชุดภาพสถานการณ์จำลองระบบนิเวศกับคำถามชวนคิด")
            with col_t2:
                target_grade = st.text_input("ระดับชั้นเป้าหมาย:", placeholder="เช่น ม.2 / ประถม 4")

            st.markdown("---")
            st.markdown("#### 🛠️ การผสานเครื่องมือ Multi-AI")
            text_ai = st.text_area(
                "📝 1. Text AI (เครื่องมือที่ใช้ + สคริปต์คำถามกระตุ้นคิด หรือ รูบริกประเมิน):",
                placeholder="ระบุ AI ที่ใช้ (เช่น ChatGPT/Copilot/Gemini) พร้อมใส่คำถามกระตุ้นคิดหรือเกณฑ์ประเมินที่สร้าง...",
                height=90
            )

            image_ai = st.text_area(
                "🖼️ 2. Image AI (เครื่องมือที่ใช้ + Prompt สร้างภาพสื่อ/ใบงาน):",
                placeholder="ระบุ AI ที่ใช้ (เช่น Midjourney/Canva AI/Bing Image Creator) พร้อม Prompt ที่ใช้สร้างภาพประกอบ...",
                height=90
            )

            fact_check = st.text_area(
                "🔍 3. Fact-checking & Verification (วิธีการตรวจสอบความถูกต้องทางวิชาการ):",
                placeholder="ระบุวิธีตรวจเช็ก เช่น ค้นเทียบกับตำรา สพฐ., เช็กความสมจริงของภาพ, ตรวจสอบศัพท์วิชาการ...",
                height=80
            )

            st.markdown("---")
            st.markdown("#### 📋 1-Page AI-Integrated Innovation Blueprint")
            blueprint = st.text_area(
                "💡 สรุปแผนการนำนวัตกรรมชิ้นนี้ไปใช้จัดกิจกรรมการเรียนรู้จริงในห้องเรียน:",
                placeholder="อธิบายสั้นๆ: ครูจะใช้นวัตกรรมนี้ในขั้นไหนของแผนการสอน (ขั้นนำ/ขั้นสอน/ขั้นสรุป) และผู้เรียนจะได้ลงมือทำอะไร...",
                height=90
            )

            submit_btn = st.form_submit_button("🚀 ส่งผลงาน 1-Page Blueprint", use_container_width=True)

            if submit_btn:
                if not student_name or not student_id or not innovation_title or not text_ai or not blueprint:
                    st.error("⚠️ กรุณากรอกข้อมูลสำคัญให้ครบถ้วนก่อนส่งผลงานครับ")
                else:
                    save_blueprint(student_name, student_id, innovation_title, target_grade, text_ai, image_ai, fact_check, blueprint)
                    st.session_state.submitted_act4_ind = True
                    st.rerun()
    else:
        st.success("🎉 บันทึกผลงาน 1-Page Blueprint เรียบร้อยแล้ว! ผลงานของคุณขึ้นสู่หน้า Showcase แล้วครับ")
        if st.button("➕ ส่งผลงานใหม่ / แก้ไข"):
            st.session_state.submitted_act4_ind = False
            st.rerun()

# ==============================================================================
# 6. หน้าจอโปรเจกเตอร์ / Canva Embed (Live Showcase Dashboard)
# ==============================================================================
else:
    col_t, col_btn = st.columns([3, 1])
    with col_t:
        st.markdown("<div class='main-header'>📊 Showcase: 1-Page AI-Integrated Innovation Blueprints</div><div class='sub-header'>คลังต้นแบบนวัตกรรมการสอนของว่าที่ครูนวัตกรทั้ง 100 คน</div>", unsafe_allow_html=True)
    with col_btn:
        if st.button("🔄 อัปเดตข้อมูลสด (Refresh)", use_container_width=True):
            st.rerun()

    df = get_all_blueprints()

    if df.empty:
        st.warning("⏳ ยังไม่มีนักศึกษาส่งต้นแบบนวัตกรรม... สแกน QR Code ด้านล่างเพื่อเริ่มกิจกรรม")
        app_url = st.text_input("ระบุ URL ของแอปนี้เพื่อสร้าง QR Code:", "http://localhost:8501")
        qr = qrcode.make(app_url)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="สแกนเพื่อส่งผลงานกิจกรรมที่ 4", width=220)
    else:
        total_works = len(df)
        m1, m2 = st.columns([1, 3])
        m1.metric("👥 นวัตกรรมที่ส่งแล้ว", f"{total_works} ชิ้น")

        st.markdown("---")
        
        # ค้นหาและแบ่งหน้าแสดงผล
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            search_query = st.text_input("🔍 ค้นหาชื่อนักศึกษา / ชื่อนวัตกรรม / สาขา:", placeholder="พิมพ์ค้นหา...")
        with col_s2:
            items_per_page = st.selectbox("แสดงผลหน้าละ:", [10, 20, 50, 100], index=0)

        filtered_df = df
        if search_query.strip():
            filtered_df = df[
                df["student_name"].str.contains(search_query, case=False, na=False) |
                df["student_id"].str.contains(search_query, case=False, na=False) |
                df["innovation_title"].str.contains(search_query, case=False, na=False)
            ]

        st.caption(f"แสดง {min(items_per_page, len(filtered_df))} จากทั้งหมด {len(filtered_df)} ผลงาน")

        # แสดงการ์ดผลงาน 2 คอลัมน์ (โครงสร้างชิดซ้ายไม่มี Indent เพื่อป้องกันปัญหา Markdown Code Block)
        cols = st.columns(2)
        for idx, row in filtered_df.head(items_per_page).reset_index().iterrows():
            col_target = cols[idx % 2]
            with col_target:
                text_ai_clean = str(row['text_ai_content']).replace('\n', '<br>')
                image_ai_clean = str(row['image_ai_content']).replace('\n', '<br>')
                fact_check_clean = str(row['fact_check_content']).replace('\n', '<br>')
                blueprint_clean = str(row['blueprint_summary']).replace('\n', '<br>')

                card_html = (
                    f"<div class='blueprint-card'>"
                    f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;'>"
                    f"<span style='font-size:16px;font-weight:bold;color:#0284C7;'>💡 {row['innovation_title']}</span>"
                    f"<span class='badge-grade'>{row['target_grade']}</span>"
                    f"</div>"
                    f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;'>"
                    f"<span style='font-size:14px;font-weight:600;color:#1E3A8A;'>👤 {row['student_name']}</span>"
                    f"<span class='badge-user'>{row['student_id']}</span>"
                    f"</div>"
                    f"<div class='section-box'><b>📝 Text AI (คำถาม/รูบริก):</b><br>{text_ai_clean}</div>"
                    f"<div class='section-box'><b>🖼️ Image AI (สื่อประกอบ):</b><br>{image_ai_clean}</div>"
                    f"<div class='section-box'><b>🔍 Fact-checking:</b><br>{fact_check_clean}</div>"
                    f"<div class='blueprint-box'><b>📋 1-Page Blueprint (แผนการนำไปใช้):</b><br>{blueprint_clean}</div>"
                    f"</div>"
                )
                st.markdown(card_html, unsafe_allow_html=True)

        st.markdown("---")
        with st.expander("⚙️ เครื่องมือจัดการข้อมูลและส่งออกผลงานทั้งหมด (สำหรับวิทยากร)"):
            st.dataframe(df)
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลด Blueprint 100 คนเป็น Excel/CSV",
                data=csv_data,
                file_name="activity4_innovation_blueprints.csv",
                mime="text/csv"
            )
            if st.button("🗑️ ล้างข้อมูลทั้งหมดเพื่อเริ่มรอบใหม่", type="primary"):
                clear_db()
                st.rerun()
