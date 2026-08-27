import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import qrcode
from io import BytesIO
import textwrap

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(
    page_title="กิจกรรมที่ 2: วิเคราะห์กรณีศึกษา (งานเดี่ยว)",
    page_icon="⚖️",
    layout="wide"
)

# --- 2. ปรับแต่ง CSS (ล็อกสีตัวอักษรให้อ่านง่ายทุกโหมด) ---
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
    .case-card-ai {
        background-color: #FFF1F2 !important;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #FECDD3;
        border-left: 5px solid #E11D48;
        font-size: 14.5px;
        color: #1E293B !important;
        margin-bottom: 14px;
        line-height: 1.6;
    }
    .case-card-pedagogy {
        background-color: #F0FDF4 !important;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #BBF7D0;
        border-left: 5px solid #16A34A;
        font-size: 14.5px;
        color: #1E293B !important;
        margin-bottom: 14px;
        line-height: 1.6;
    }
    .analysis-card {
        background-color: #FFFFFF !important;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #E2E8F0;
        border-top: 5px solid #4F46E5;
        color: #1E293B !important;
    }
    .badge-bias {
        background-color: #FEE2E2 !important;
        color: #991B1B !important;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin-right: 4px;
        margin-bottom: 4px;
    }
    .badge-student {
        background-color: #EEF2FF !important;
        color: #3730A3 !important;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
    }
    .must-define-box {
        background-color: #F0F9FF !important;
        border-left: 3px solid #0284C7;
        padding: 10px 12px;
        border-radius: 0 8px 8px 0;
        font-size: 13.5px;
        margin-top: 10px;
        color: #0C4A6E !important;
    }
</style>
""")
st.markdown(custom_css, unsafe_allow_html=True)

# --- 3. ระบบฐานข้อมูล SQLite (ปรับแต่งรองรับ 100+ ผู้ใช้พร้อมกัน) ---
DB_NAME = "case_study_act2_individual.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=30.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")  # ป้องกันปัญหา DB Lock เมื่อส่งพร้อมกัน
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS individual_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT,
                student_id TEXT,
                bias_dimensions TEXT,
                weaknesses TEXT,
                must_define_first TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def save_analysis(student_name, student_id, bias_dimensions, weaknesses, must_define_first):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO individual_analyses (student_name, student_id, bias_dimensions, weaknesses, must_define_first)
            VALUES (?, ?, ?, ?, ?)
        """, (student_name.strip(), student_id.strip(), ", ".join(bias_dimensions), weaknesses.strip(), must_define_first.strip()))
        conn.commit()

def get_all_analyses():
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM individual_analyses ORDER BY id DESC", conn)
    return df

def clear_db():
    with get_connection() as conn:
        conn.execute("DELETE FROM individual_analyses")
        conn.commit()

init_db()

# --- 4. เมนูด้านข้าง ---
st.sidebar.title("⚖️ Activity 2 (งานเดี่ยว)")
view_mode = st.sidebar.radio(
    "เลือกมุมมองหน้าจอ:",
    ["📱 สำหรับนักศึกษา (ส่งงานเดี่ยว)", "📊 จอโปรเจกเตอร์วิทยากร (Live Dashboard)"]
)

# ==============================================================================
# 5. หน้านักศึกษา (Individual Submission)
# ==============================================================================
if view_mode == "📱 สำหรับนักศึกษา (ส่งงานเดี่ยว)":
    header_html = textwrap.dedent("""
    <div class='main-header'>⚖️ กิจกรรมที่ 2: วิเคราะห์กรณีศึกษา (งานเดี่ยว)</div>
    <div class='sub-header'>"Pedagogy Leads, AI Follows" (ศาสตร์การสอนต้องนำ เทคโนโลยีต้องตาม)</div>
    """)
    st.markdown(header_html, unsafe_allow_html=True)

    # กล่องกรณีศึกษา (แก้ปัญหาสีฟอนต์กลืนกับพื้นหลังแล้ว)
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        case1_html = textwrap.dedent("""
        <div class='case-card-ai'>
            <b style='color: #9F1239; font-size: 15px;'>📕 แผนที่ 1: AI-Driven (ให้ AI คิดแทน 100%)</b><br>
            ใช้ Prompt กว้างๆ สั่งให้ AI สร้างแผนการสอนที่สมบูรณ์แบบตามทฤษฎี แต่ใช้อุปกรณ์ที่โรงเรียนไม่มี และไม่เข้ากับบริบทเด็กในพื้นที่
        </div>
        """)
        st.markdown(case1_html, unsafe_allow_html=True)
    with col_c2:
        case2_html = textwrap.dedent("""
        <div class='case-card-pedagogy'>
            <b style='color: #166534; font-size: 15px;'>📗 แผนที่ 2: Pedagogy-Driven (ครูนำ AI ตาม)</b><br>
            ครูกำหนดเป้าหมายและข้อจำกัดก่อน (Pedagogy) แล้วใช้ AI ช่วยคิดเกมและการประเมินผลที่สอดคล้องกับเด็กในชุมชน
        </div>
        """)
        st.markdown(case2_html, unsafe_allow_html=True)

    if "submitted_act2_ind" not in st.session_state:
        st.session_state.submitted_act2_ind = False

    if not st.session_state.submitted_act2_ind:
        with st.form("individual_form"):
            st.markdown("#### 👤 ข้อมูลผู้ส่งงาน")
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                student_name = st.text_input("ชื่อ - นามสกุล:", placeholder="เช่น นายสมชาย ใจดี")
            with col_u2:
                student_id = st.text_input("รหัสนักศึกษา / สาขาวิชา:", placeholder="เช่น 66123456 เอกคอมพิวเตอร์ศึกษา")

            st.markdown("---")
            st.markdown("#### 🔍 ชวนคิด: ท่านคิดว่าแผนที่ 1 มีจุดบอดและอคติ (Bias) ในมิติใดบ้าง?")
            bias_options = [
                "💻 บริบทความพร้อมด้านอุปกรณ์และโครงสร้างพื้นฐาน (Digital Divide)",
                "🌾 ความสอดคล้องกับบริบทชุมชนและวัฒนธรรมท้องถิ่น (Cultural/Context Bias)",
                "🎯 ความเข้าใจความต้องการจริงของเด็ก (Lack of Empathy)",
                "⏱️ ความเป็นไปได้ในการจัดการเรียนรู้จริงในห้องเรียน (Practical Feasibility)",
                "📖 การยึดติดกับทฤษฎีสากลมากเกินไปโดยไม่ปรับบริบท (Western Model Bias)"
            ]
            selected_biases = st.multiselect(
                "เลือกมิติจุดบอด/อคติที่ท่านพบ (เลือกได้มากกว่า 1 ข้อ):",
                options=bias_options
            )

            weaknesses = st.text_area(
                "💬 อธิบายเจาะลึกจุดบอดของแผนที่ 1 ในมุมมองของท่าน:",
                placeholder="อธิบายเหตุผล เช่น การให้ AI คิดโดยไม่มีขอบเขต ทำให้ได้กิจกรรมหรูหราที่เด็กเข้าไม่ถึง...",
                height=90
            )

            st.markdown("---")
            st.markdown("#### 💡 บทเรียนสำหรับครูนวัตกร")
            must_define = st.text_area(
                "🔑 สิ่งที่ครู 'ต้องกำหนดให้ชัดเจนก่อนสั่งการ AI' คืออะไร?",
                placeholder="เช่น กำหนดวัตถุประสงค์การเรียนรู้ (KPA), ความพร้อมของอุปกรณ์, และพฤติกรรมผู้เรียน...",
                height=80
            )

            submit_btn = st.form_submit_button("🚀 ส่งคำตอบของฉัน", use_container_width=True)

            if submit_btn:
                if not student_name or not student_id or not selected_biases or not weaknesses or not must_define:
                    st.error("⚠️ กรุณากรอกข้อมูลให้ครบถ้วนทุกช่องก่อนกดส่งครับ")
                else:
                    save_analysis(student_name, student_id, selected_biases, weaknesses, must_define)
                    st.session_state.submitted_act2_ind = True
                    st.rerun()
    else:
        st.success("🎉 บันทึกคำตอบของคุณเรียบร้อยแล้ว ข้อมูลถูกส่งขึ้นระบบแล้วครับ!")
        if st.button("➕ ส่งคำตอบใหม่ / แก้ไข"):
            st.session_state.submitted_act2_ind = False
            st.rerun()

# ==============================================================================
# 6. หน้าจอโปรเจกเตอร์ / Canva Embed (Live Dashboard รองรับ 100 คน)
# ==============================================================================
else:
    col_t, col_btn = st.columns([3, 1])
    with col_t:
        dash_header = textwrap.dedent("""
        <div class='main-header'>📊 Live Insights: เจาะลึกจุดบอด "AI-Driven vs Pedagogy-Driven"</div>
        <div class='sub-header'>สรุปภาพรวมความคิดเห็นของนักศึกษาทั้ง 100 คน แบบเรียลไทม์</div>
        """)
        st.markdown(dash_header, unsafe_allow_html=True)
    with col_btn:
        if st.button("🔄 อัปเดตข้อมูลสด (Refresh)", use_container_width=True):
            st.rerun()

    df = get_all_analyses()

    if df.empty:
        st.warning("⏳ ยังไม่มีนักศึกษาส่งคำตอบ... สแกน QR Code ด้านล่างเพื่อเริ่มกิจกรรม")
        app_url = st.text_input("ระบุ URL ของแอปนี้เพื่อสร้าง QR Code:", "http://localhost:8501")
        qr = qrcode.make(app_url)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="สแกนเพื่อร่วมทำกิจกรรมที่ 2", width=220)
    else:
        # แถบสรุปจำนวน
        total_responses = len(df)
        m1, m2 = st.columns([1, 3])
        m1.metric("👥 ส่งคำตอบแล้ว", f"{total_responses} คน")
        
        # ประมวลผลกราฟสรุป Bias (เหมาะมากสำหรับการสรุปผล 100 คน)
        all_biases = []
        for b_str in df["bias_dimensions"].dropna():
            all_biases.extend([b.strip() for b in b_str.split(",") if b.strip()])
        
        bias_df = pd.Series(all_biases).value_counts().reset_index()
        bias_df.columns = ["มิติจุดบอด/อคติ", "จำนวนคนโหวต"]

        fig_bar = px.bar(
            bias_df,
            x="จำนวนคนโหวต",
            y="มิติจุดบอด/อคติ",
            orientation="h",
            title="📊 สถิติมิติจุดบอดที่นักศึกษาค้นพบมากที่สุด",
            color="จำนวนคนโหวต",
            color_continuous_scale="Reds"
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=280, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        
        # ส่วนค้นหาและแสดงผลการ์ดรายบุคคล (เพื่อประสิทธิภาพในการแสดงผล 100 รายการ)
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            search_query = st.text_input("🔍 ค้นหาชื่อนักศึกษา / รหัส / สาขา:", placeholder="พิมพ์ค้นหา...")
        with col_s2:
            items_per_page = st.selectbox("แสดงผลหน้าละ:", [10, 20, 50, 100], index=0)

        # กรองข้อมูล
        filtered_df = df
        if search_query.strip():
            filtered_df = df[
                df["student_name"].str.contains(search_query, case=False, na=False) |
                df["student_id"].str.contains(search_query, case=False, na=False)
            ]

        st.caption(f"แสดง {min(items_per_page, len(filtered_df))} จากทั้งหมด {len(filtered_df)} รายการ")

        # แสดงการ์ด 2 คอลัมน์
        cols = st.columns(2)
        for idx, row in filtered_df.head(items_per_page).reset_index().iterrows():
            col_target = cols[idx % 2]
            with col_target:
                badges_html = "".join([f"<span class='badge-bias'>⚠️ {b.strip()}</span>" for b in row['bias_dimensions'].split(",") if b.strip()])
                
                card_html = textwrap.dedent(f"""
                <div class='analysis-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                        <span style='font-size: 16px; font-weight: bold; color: #1E3A8A;'>👤 {row['student_name']}</span>
                        <span class='badge-student'>{row['student_id']}</span>
                    </div>
                    <div style='margin-bottom: 8px;'>{badges_html}</div>
                    
                    <div style='font-size: 13.5px; color: #334155; margin-bottom: 8px;'>
                        <b>🔍 จุดบอดของแผนที่ 1:</b><br>{row['weaknesses']}
                    </div>
                    
                    <div class='must-define-box'>
                        <b>🔑 สิ่งที่ครูต้องกำหนดก่อนใช้ AI:</b><br>{row['must_define_first']}
                    </div>
                </div>
                """)
                st.markdown(card_html, unsafe_allow_html=True)

        # เมนูจัดการและ Export สำหรับวิทยากร
        st.markdown("---")
        with st.expander("⚙️ เครื่องมือจัดการข้อมูลและส่งออกคะแนน (สำหรับวิทยากร)"):
            st.dataframe(df)
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลดรายชื่อและคำตอบ 100 คนเป็น Excel/CSV",
                data=csv_data,
                file_name="activity2_individual_results.csv",
                mime="text/csv"
            )
            if st.button("🗑️ ล้างข้อมูลทั้งหมดเพื่อเริ่มรอบใหม่", type="primary"):
                clear_db()
                st.rerun()
