import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import qrcode
from io import BytesIO

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(
    page_title="กิจกรรมที่ 6: Meta-Reflection (AAR)",
    page_icon="💖",
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
.quote-box {
    background-color: #F0FDF4 !important;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #BBF7D0;
    border-left: 5px solid #16A34A;
    font-size: 15px;
    color: #14532D !important;
    margin-bottom: 16px;
    line-height: 1.6;
}
.reflection-card {
    background-color: #FFFFFF !important;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border: 1px solid #E2E8F0;
    border-top: 5px solid #EC4899;
    color: #1E293B !important;
}
.badge-user {
    background-color: #FDF2F8 !important;
    color: #9D174D !important;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
}
.badge-kw {
    background-color: #EFF6FF !important;
    color: #1D4ED8 !important;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin-right: 4px;
    margin-bottom: 4px;
}
.pledge-box {
    background-color: #FFFBEB !important;
    border: 1px dashed #F59E0B;
    padding: 12px;
    border-radius: 8px;
    font-size: 14px;
    color: #92400E !important;
    margin-top: 8px;
    font-weight: 600;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- 3. ระบบฐานข้อมูล SQLite (รองรับ 100+ คนพร้อมกัน) ---
DB_NAME = "reflection_act6_100users.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=30.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")  # ป้องกัน DB Lock
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meta_reflections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT,
                student_id TEXT,
                keywords TEXT,
                reflection_story TEXT,
                teacher_pledge TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def save_reflection(student_name, student_id, keywords_list, reflection_story, teacher_pledge):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO meta_reflections (
                student_name, student_id, keywords, reflection_story, teacher_pledge
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            student_name.strip(), student_id.strip(), ", ".join(keywords_list),
            reflection_story.strip(), teacher_pledge.strip()
        ))
        conn.commit()

def get_all_reflections():
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM meta_reflections ORDER BY id DESC", conn)
    return df

def clear_db():
    with get_connection() as conn:
        conn.execute("DELETE FROM meta_reflections")
        conn.commit()

init_db()

# --- 4. รายการ Keyword มาตรฐาน (12 ตัวเลือก) ---
PRESET_KEYWORDS = [
    "ความเข้าอกเข้าใจและเมตตา (Empathy)",
    "การสร้างแรงบันดาลใจและปลุกพลัง (Inspiration)",
    "การเป็นแบบอย่างทางจริยธรรม (Role Model)",
    "การรับฟังอย่างลึกซึ้งและพื้นที่ปลอดภัย (Deep Listening)",
    "สายสัมพันธ์และการสัมผัสใจมนุษย์ (Human Connection)",
    "การประคองอารมณ์และจิตใจผู้เรียน (Emotional Support)",
    "จิตวิญญาณและความรักในวิชาชีพ (Teacher's Soul)",
    "การแก้ปัญหาเฉพาะหน้าด้วยวิจารณญาณ (Critical Judgment)",
    "การโอบอุ้มเด็กกลุ่มเปราะบาง (Inclusivity & Care)",
    "การสร้างศรัทธาและความไว้วางใจ (Trust Building)",
    "การโค้ชชีวิตและให้คำปรึกษา (Life Coaching)",
    "อารมณ์ขันและบรรยากาศความสุข (Human Warmth)",
    "✨ อื่น ๆ (ระบุคีย์เวิร์ดด้วยตนเอง)"
]

# --- 5. เมนูด้านข้าง ---
st.sidebar.title("💖 Activity 6 Control")
view_mode = st.sidebar.radio(
    "เลือกมุมมองหน้าจอ:",
    ["📱 สำหรับนักศึกษา (สะท้อนคิด AAR)", "📊 จอโปรเจกเตอร์วิทยากร (Live Word Cloud & Wall)"]
)

# ==============================================================================
# 6. หน้านักศึกษา (Individual Submission)
# ==============================================================================
if view_mode == "📱 สำหรับนักศึกษา (สะท้อนคิด AAR)":
    st.markdown("<div class='main-header'>💖 กิจกรรมที่ 6: Meta-Reflection (AAR)</div><div class='sub-header'>สรุปบทเรียนการสะท้อนคิดสู่จิตวิญญาณความเป็นครูตาม PTRU Model</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='quote-box'>
        <b>🎯 คำถามสำคัญทิ้งท้าย:</b><br>
        <i>"ทักษะอะไรของครู ที่ AI จะไม่มีวันเข้ามาแทนที่ได้?"</i><br>
        <span style='font-size:13.5px;'>ร่วมแลกเปลี่ยนและสะท้อนมุมมองด้าน <b>'จิตวิญญาณความเป็นครู'</b> ตามโมเดล PTRU สมรรถนะที่ 17</span>
    </div>
    """, unsafe_allow_html=True)

    if "submitted_act6_ind" not in st.session_state:
        st.session_state.submitted_act6_ind = False

    if not st.session_state.submitted_act6_ind:
        with st.form("reflection_form"):
            st.markdown("#### 👤 ข้อมูลผู้สะท้อนคิด")
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                student_name = st.text_input("ชื่อ - นามสกุล:", placeholder="เช่น นายสมชาย ใจดี")
            with col_u2:
                student_id = st.text_input("รหัสนักศึกษา / สาขาวิชา:", placeholder="เช่น 66123456 เอกคอมพิวเตอร์ศึกษา")

            st.markdown("---")
            st.markdown("#### 🏷️ 1. เลือกคีย์เวิร์ดทักษะที่ AI แทนไม่ได้ (เลือกได้ 1–3 ข้อ)")
            selected_kw = st.multiselect(
                "เลือกคีย์เวิร์ดที่ตรงใจท่านที่สุด:",
                options=PRESET_KEYWORDS,
                default=[PRESET_KEYWORDS[0]]
            )

            custom_kw_input = ""
            if "✨ อื่น ๆ (ระบุคีย์เวิร์ดด้วยตนเอง)" in selected_kw:
                custom_kw_input = st.text_input(
                    "ระบุคีย์เวิร์ดของท่านเอง (สั้นๆ 1-2 คำ):",
                    placeholder="เช่น การกอดปลอบใจ, แววตาแห่งความหวัง"
                )

            st.markdown("---")
            st.markdown("#### 💬 2. การสะท้อนคิดเชิงลึก (Reflection Story)")
            reflection_story = st.text_area(
                "ทำไมทักษะนี้จึงสำคัญ และท่านจะนำไปใช้ดูแลผู้เรียนจริงในห้องเรียนอย่างไร?",
                placeholder="เล่ามุมมองหรือเหตุการณ์สั้นๆ เช่น AI อาจตรวจข้อสอบได้เร็วกว่า แต่เมื่อเด็กกำลังร้องไห้หรือหมดไฟ มีเพียงครูที่เป็นมนุษย์เท่านั้นที่จะสัมผัสใจและประคองเขาขึ้นมาได้...",
                height=90
            )

            st.markdown("#### 📜 3. คำมั่นสัญญาครูนวัตกร (Teacher's Pledge)")
            teacher_pledge = st.text_input(
                "💡 คำมั่นสัญญาของฉัน: 'ในฐานะครูนวัตกร ฉันจะเป็นครูที่...'",
                placeholder="เช่น ฉันจะเป็นครูที่ใช้ AI ช่วยทุ่นแรง เพื่อเอาเวลาทั้งหมดไปมอบความรักและรับฟังเด็กๆ ทุกคน"
            )

            submit_btn = st.form_submit_button("🚀 ส่งคำสะท้อนคิดขึ้นกำแพง AAR", use_container_width=True)

            if submit_btn:
                # รวบรวมคีย์เวิร์ด
                final_keywords = [k for k in selected_kw if k != "✨ อื่น ๆ (ระบุคีย์เวิร์ดด้วยตนเอง)"]
                if custom_kw_input.strip():
                    final_keywords.append(custom_kw_input.strip())

                if not student_name or not student_id or not final_keywords or not reflection_story or not teacher_pledge:
                    st.error("⚠️ กรุณากรอกข้อมูลให้ครบถ้วนทุกช่องก่อนส่งครับ")
                else:
                    save_reflection(student_name, student_id, final_keywords, reflection_story, teacher_pledge)
                    st.session_state.submitted_act6_ind = True
                    st.rerun()
    else:
        st.success("🎉 บันทึกคำสะท้อนคิดเรียบร้อยแล้ว ขอบคุณที่ร่วมส่งต่อพลังความเป็นครูครับ!")
        if st.button("➕ ส่งคำสะท้อนคิดใหม่ / แก้ไข"):
            st.session_state.submitted_act6_ind = False
            st.rerun()

# ==============================================================================
# 7. หน้าจอโปรเจกเตอร์ / Canva Embed (Live Word Cloud & Reflection Wall)
# ==============================================================================
else:
    col_t, col_btn = st.columns([3, 1])
    with col_t:
        st.markdown("<div class='main-header'>📊 Live Word Cloud & Pledge Wall (AAR)</div><div class='sub-header'>พลังสะท้อนคิดด้าน 'จิตวิญญาณความเป็นครู' ของว่าที่บัณฑิตครุศาสตร์ทั้ง 100 คน</div>", unsafe_allow_html=True)
    with col_btn:
        if st.button("🔄 อัปเดตข้อมูลสด (Refresh)", use_container_width=True):
            st.rerun()

    df = get_all_reflections()

    if df.empty:
        st.warning("⏳ ยังไม่มีการส่งคำสะท้อนคิด... สแกน QR Code ด้านล่างเพื่อเริ่มกิจกรรม")
        app_url = st.text_input("ระบุ URL ของแอปนี้เพื่อสร้าง QR Code:", "http://localhost:8501")
        qr = qrcode.make(app_url)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="สแกนเพื่อร่วมสะท้อนคิดกิจกรรมที่ 6", width=220)
    else:
        total_users = len(df)
        m1, m2 = st.columns([1, 3])
        m1.metric("👥 ผู้ร่วมสะท้อนคิด", f"{total_users} คน")

        # ประมวลผลคีย์เวิร์ดทั้งหมดสำหรับทำ Word Cloud / Frequency Report
        all_kw_list = []
        for kw_str in df["keywords"].dropna():
            all_kw_list.extend([k.strip() for k in kw_str.split(",") if k.strip()])
        
        kw_counts = pd.Series(all_kw_list).value_counts().reset_index()
        kw_counts.columns = ["ทักษะที่ AI แทนไม่ได้", "จำนวนครั้งที่เลือก"]

        # กราฟแท่งสีสันสดใสแนว Word-Ranking
        fig_kw = px.bar(
            kw_counts.head(10),
            x="จำนวนครั้งที่เลือก",
            y="ทักษะที่ AI แทนไม่ได้",
            orientation="h",
            title="☁️ Top Keywords: ทักษะและจิตวิญญาณครูที่ AI ไม่มีวันแทนที่ได้",
            color="จำนวนครั้งที่เลือก",
            color_continuous_scale="Purples"
        )
        fig_kw.update_layout(yaxis={'categoryorder':'total ascending'}, height=320, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_kw, use_container_width=True)

        st.markdown("---")
        st.markdown("### 📜 กำแพงคำมั่นสัญญาและการสะท้อนคิด (Reflection Wall)")

        # ค้นหาและแบ่งหน้าแสดงผล
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            search_query = st.text_input("🔍 ค้นหาชื่อ / คีย์เวิร์ด / คำมั่นสัญญา:", placeholder="พิมพ์ค้นหา...")
        with col_s2:
            items_per_page = st.selectbox("แสดงผลหน้าละ:", [10, 20, 50, 100], index=0)

        filtered_df = df
        if search_query.strip():
            filtered_df = df[
                df["student_name"].str.contains(search_query, case=False, na=False) |
                df["student_id"].str.contains(search_query, case=False, na=False) |
                df["keywords"].str.contains(search_query, case=False, na=False) |
                df["teacher_pledge"].str.contains(search_query, case=False, na=False)
            ]

        st.caption(f"แสดง {min(items_per_page, len(filtered_df))} จากทั้งหมด {len(filtered_df)} รายการ")

        # แสดงการ์ด 2 คอลัมน์ (โครงสร้างชิดซ้ายไม่มี Indent เพื่อป้องกันปัญหา Markdown Code Block)
        cols = st.columns(2)
        for idx, row in filtered_df.head(items_per_page).reset_index().iterrows():
            col_target = cols[idx % 2]
            with col_target:
                badges_html = "".join([f"<span class='badge-kw'>🏷️ {k.strip()}</span>" for k in str(row['keywords']).split(",") if k.strip()])
                story_clean = str(row['reflection_story']).replace('\n', '<br>')
                pledge_clean = str(row['teacher_pledge']).replace('\n', '<br>')

                card_html = (
                    f"<div class='reflection-card'>"
                    f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>"
                    f"<span style='font-size:16px;font-weight:bold;color:#9D174D;'>👤 {row['student_name']}</span>"
                    f"<span class='badge-user'>{row['student_id']}</span>"
                    f"</div>"
                    f"<div style='margin-bottom:8px;'>{badges_html}</div>"
                    f"<div style='font-size:13.5px;color:#1E293B;margin-bottom:8px;'><b>💬 มุมมองการสะท้อนคิด:</b><br>{story_clean}</div>"
                    f"<div class='pledge-box'>🌟 <b>คำมั่นสัญญาครูนวัตกร:</b><br>\"{pledge_clean}\"</div>"
                    f"</div>"
                )
                st.markdown(card_html, unsafe_allow_html=True)

        st.markdown("---")
        with st.expander("⚙️ เครื่องมือจัดการข้อมูลและส่งออกผลการสะท้อนคิด (สำหรับวิทยากร)"):
            st.dataframe(df)
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลดผล AAR 100 คนเป็น Excel/CSV",
                data=csv_data,
                file_name="activity6_meta_reflection_aar.csv",
                mime="text/csv"
            )
            if st.button("🗑️ ล้างข้อมูลทั้งหมดเพื่อเริ่มรอบใหม่", type="primary"):
                clear_db()
                st.rerun()
