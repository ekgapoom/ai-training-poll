import streamlit as st
import sqlite3
import pandas as pd
import qrcode
from io import BytesIO

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(
    page_title="กิจกรรมที่ 5: Peer & AI Pitching Challenge",
    page_icon="🎤",
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
.pitch-card {
    background-color: #FFFFFF !important;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border: 1px solid #E2E8F0;
    border-top: 5px solid #8B5CF6;
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
.badge-score {
    background-color: #FEF3C7 !important;
    color: #92400E !important;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 12.5px;
    font-weight: bold;
}
.ai-feedback-box {
    background-color: #FEF2F2 !important;
    border-left: 3px solid #EF4444;
    padding: 10px;
    border-radius: 0 6px 6px 0;
    font-size: 13.5px;
    color: #1E293B !important;
    margin-bottom: 8px;
}
.peer-feedback-box {
    background-color: #F0FDF4 !important;
    border-left: 3px solid #22C55E;
    padding: 10px;
    border-radius: 0 6px 6px 0;
    font-size: 13.5px;
    color: #1E293B !important;
    margin-bottom: 8px;
}
.action-plan-box {
    background-color: #F5F3FF !important;
    border: 1px dashed #8B5CF6;
    padding: 12px;
    border-radius: 8px;
    font-size: 13.5px;
    color: #4C1D95 !important;
    margin-top: 8px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- 3. ระบบฐานข้อมูล SQLite (รองรับ 100+ คนพร้อมกัน) ---
DB_NAME = "pitching_act5_100users.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=30.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")  # รองรับ High Concurrency
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pitching_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT,
                student_id TEXT,
                innovation_title TEXT,
                ai_critique TEXT,
                peer_feedback TEXT,
                action_plan TEXT,
                readiness_score INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def save_review(student_name, student_id, innovation_title, ai_critique, peer_feedback, action_plan, readiness_score):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO pitching_reviews (
                student_name, student_id, innovation_title, 
                ai_critique, peer_feedback, action_plan, readiness_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            student_name.strip(), student_id.strip(), innovation_title.strip(),
            ai_critique.strip(), peer_feedback.strip(), action_plan.strip(), readiness_score
        ))
        conn.commit()

def get_all_reviews():
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM pitching_reviews ORDER BY id DESC", conn)
    return df

def clear_db():
    with get_connection() as conn:
        conn.execute("DELETE FROM pitching_reviews")
        conn.commit()

init_db()

# --- 4. เมนูด้านข้าง ---
st.sidebar.title("🎤 Activity 5 Control")
view_mode = st.sidebar.radio(
    "เลือกมุมมองหน้าจอ:",
    ["📱 สำหรับนักศึกษา (บันทึกผล Pitching & Feedback)", "📊 จอโปรเจกเตอร์วิทยากร (Live Showcase)"]
)

# ==============================================================================
# 5. หน้านักศึกษา (Individual Submission)
# ==============================================================================
if view_mode == "📱 สำหรับนักศึกษา (บันทึกผล Pitching & Feedback)":
    st.markdown("<div class='main-header'>🎤 กิจกรรมที่ 5: Peer & AI Pitching Challenge</div><div class='sub-header'>เป้าหมาย: รับฟังและสังเคราะห์ข้อเสนอแนะรอบทิศทาง (AI Reviewer + Peer Feedback)</div>", unsafe_allow_html=True)

    with st.expander("💡 คลิกเพื่อคัดลอก 'Prompt สวมบทบาท AI เป็นกรรมการผู้ทรงคุณวุฒิ'", expanded=False):
        prompt_reviewer = (
            "จงสวมบทบาทเป็น 'กรรมการผู้ทรงคุณวุฒิด้านนวัตกรรมการศึกษา' ที่มีมาตรฐานสูงและเข้มงวด "
            "ช่วยวิพากษ์และชี้จุดบอด (Critical Review) ของนวัตกรรมการสอนต่อไปนี้ใน 3 มิติ: "
            "1) ความเป็นไปได้ในการใช้ในห้องเรียนจริง "
            "2) จุดอ่อนด้านการวัดและประเมินผล "
            "3) สิ่งที่อาจทำให้ผู้เรียนไม่บรรลุวัตถุประสงค์ "
            "พร้อมให้ข้อเสนอแนะแนวทางแก้ไขสั้นๆ 2 ข้อ (นี่คือไอเดียนวัตกรรมของฉัน: [ใส่นวัตกรรมของคุณที่นี่])"
        )
        st.code(prompt_reviewer, language="text")
        st.caption("👉 คัดลอกข้อความนี้ไปวางใน AI เพื่อให้ AI วิพากษ์จุดบอดของนวัตกรรม")

    if "submitted_act5_ind" not in st.session_state:
        st.session_state.submitted_act5_ind = False

    if not st.session_state.submitted_act5_ind:
        with st.form("pitching_form"):
            st.markdown("#### 👤 ข้อมูลผู้นำเสนอ")
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                student_name = st.text_input("ชื่อ - นามสกุล / ชื่อกลุ่ม:", placeholder="เช่น นายสมชาย ใจดี หรือ กลุ่ม 2 เอกคณิตฯ")
            with col_u2:
                student_id = st.text_input("รหัสนักศึกษา / สาขาวิชา:", placeholder="เช่น 66123456 เอกคอมพิวเตอร์ศึกษา")

            innovation_title = st.text_input("💡 ชื่อนวัตกรรมการสอนที่นำเสนอ:", placeholder="เช่น บทเรียนสถานการณ์จำลอง AI เรื่องการเปลี่ยนแปลงสภาพภูมิอากาศ")

            st.markdown("---")
            st.markdown("#### 🤖 1. AI as a Critical Reviewer (มุมมองเชิงเหตุผล/ชี้จุดบอด)")
            ai_critique = st.text_area(
                "สรุปจุดบอดและข้อเสนอแนะที่ได้จาก AI Reviewer:",
                placeholder="เช่น AI ชี้ว่าเวลา 50 นาทีอาจไม่พอสำหรับกิจกรรมกลุ่มย่อย และเกณฑ์ประเมินยังกว้างเกินไป...",
                height=80
            )

            st.markdown("#### 👥 2. Peer & Mentor Feedback (มุมมองความเห็นอกเห็นใจจากมนุษย์)")
            peer_feedback = st.text_area(
                "สรุปข้อเสนอแนะและเสียงสะท้อนจากเพื่อนในห้องและอาจารย์:",
                placeholder="เช่น เพื่อนชอบความน่าสนใจของภาพประกอบ แต่เสนอว่าควรมีใบงานสรุปย่อให้นักเรียนที่เรียนช้า...",
                height=80
            )

            st.markdown("---")
            st.markdown("#### 🔄 3. การสังเคราะห์แนวทางปรับปรุง (Action Plan)")
            action_plan = st.text_area(
                "🔑 จากคำวิจารณ์ทั้งหมด สิ่งสำคัญที่สุด 2 ประการที่ท่านจะนำไป 'ปรับปรุงนวัตกรรม' ให้สมบูรณ์คืออะไร?",
                placeholder="เช่น 1. ปรับลดขั้นตอนกิจกรรมให้กระชับลง 15 นาที  2. เพิ่มรูบริกประเมินแบบแยกรายบุคคล...",
                height=90
            )

            readiness_score = st.slider(
                "⭐ ประเมินระดับความพร้อมของนวัตกรรมชิ้นนี้ก่อนนำไปทดลองสอนจริง (1 = ต้องรื้อใหม่, 10 = พร้อมใช้ทันที):",
                min_value=1, max_value=10, value=8
            )

            submit_btn = st.form_submit_button("🚀 ส่งผลการสังเคราะห์ขึ้นระบบ", use_container_width=True)

            if submit_btn:
                if not student_name or not innovation_title or not ai_critique or not action_plan:
                    st.error("⚠️ กรุณากรอกข้อมูลสำคัญให้ครบถ้วนก่อนส่งครับ")
                else:
                    save_review(student_name, student_id, innovation_title, ai_critique, peer_feedback, action_plan, readiness_score)
                    st.session_state.submitted_act5_ind = True
                    st.rerun()
    else:
        st.success("🎉 บันทึกผลการสังเคราะห์ Feedback เรียบร้อยแล้ว! ข้อมูลของคุณขึ้นสู่หน้า Showcase แล้วครับ")
        if st.button("➕ ส่งผลงานเพิ่มเติม / แก้ไข"):
            st.session_state.submitted_act5_ind = False
            st.rerun()

# ==============================================================================
# 6. หน้าจอโปรเจกเตอร์ / Canva Embed (Live Showcase Dashboard)
# ==============================================================================
else:
    col_t, col_btn = st.columns([3, 1])
    with col_t:
        st.markdown("<div class='main-header'>📊 Live Showcase: Peer & AI Pitching Feedback</div><div class='sub-header'>ศูนย์รวมบทวิพากษ์และการสังเคราะห์แนวทางพัฒนานวัตกรรมของนักศึกษา</div>", unsafe_allow_html=True)
    with col_btn:
        if st.button("🔄 อัปเดตข้อมูลสด (Refresh)", use_container_width=True):
            st.rerun()

    df = get_all_reviews()

    if df.empty:
        st.warning("⏳ ยังไม่มีการส่งผล Feedback... สแกน QR Code ด้านล่างเพื่อเริ่มกิจกรรม")
        app_url = st.text_input("ระบุ URL ของแอปนี้เพื่อสร้าง QR Code:", "http://localhost:8501")
        qr = qrcode.make(app_url)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="สแกนเพื่อร่วมทำกิจกรรมที่ 5", width=220)
    else:
        total_items = len(df)
        avg_score = df["readiness_score"].mean()
        
        m1, m2 = st.columns(2)
        m1.metric("👥 ส่งผลการสังเคราะห์แล้ว", f"{total_items} คน")
        m2.metric("⭐ ความพร้อมนวัตกรรมเฉลี่ย", f"{avg_score:.1f} / 10")

        st.markdown("---")
        
        # ค้นหาและแบ่งหน้าแสดงผล
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            search_query = st.text_input("🔍 ค้นหาชื่อ / ชื่อนวัตกรรม / สาขา:", placeholder="พิมพ์ค้นหา...")
        with col_s2:
            items_per_page = st.selectbox("แสดงผลหน้าละ:", [10, 20, 50, 100], index=0)

        filtered_df = df
        if search_query.strip():
            filtered_df = df[
                df["student_name"].str.contains(search_query, case=False, na=False) |
                df["student_id"].str.contains(search_query, case=False, na=False) |
                df["innovation_title"].str.contains(search_query, case=False, na=False)
            ]

        st.caption(f"แสดง {min(items_per_page, len(filtered_df))} จากทั้งหมด {len(filtered_df)} รายการ")

        # แสดงการ์ด 2 คอลัมน์ (โครงสร้างชิดซ้ายไม่มี Indent เพื่อป้องกันปัญหา Markdown Code Block)
        cols = st.columns(2)
        for idx, row in filtered_df.head(items_per_page).reset_index().iterrows():
            col_target = cols[idx % 2]
            with col_target:
                ai_c = str(row['ai_critique']).replace('\n', '<br>')
                peer_c = str(row['peer_feedback']).replace('\n', '<br>')
                action_c = str(row['action_plan']).replace('\n', '<br>')

                card_html = (
                    f"<div class='pitch-card'>"
                    f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;'>"
                    f"<span style='font-size:16px;font-weight:bold;color:#7C3AED;'>🎤 {row['innovation_title']}</span>"
                    f"<span class='badge-score'>ความพร้อม: {row['readiness_score']}/10 ⭐</span>"
                    f"</div>"
                    f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;'>"
                    f"<span style='font-size:14px;font-weight:600;color:#1E3A8A;'>👤 {row['student_name']}</span>"
                    f"<span class='badge-user'>{row['student_id']}</span>"
                    f"</div>"
                    f"<div class='ai-feedback-box'><b>🤖 AI Critical Reviewer (ชี้จุดบอด):</b><br>{ai_c}</div>"
                    f"<div class='peer-feedback-box'><b>👥 Peer & Mentor Feedback (เสียงสะท้อน):</b><br>{peer_c}</div>"
                    f"<div class='action-plan-box'><b>🔄 Action Plan (แผนการปรับปรุงนวัตกรรม):</b><br>{action_c}</div>"
                    f"</div>"
                )
                st.markdown(card_html, unsafe_allow_html=True)

        st.markdown("---")
        with st.expander("⚙️ เครื่องมือจัดการข้อมูลและส่งออกคะแนน (สำหรับวิทยากร)"):
            st.dataframe(df)
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลดผลการสังเคราะห์ Feedback 100 คนเป็น Excel/CSV",
                data=csv_data,
                file_name="activity5_pitching_reviews.csv",
                mime="text/csv"
            )
            if st.button("🗑️ ล้างข้อมูลทั้งหมดเพื่อเริ่มรอบใหม่", type="primary"):
                clear_db()
                st.rerun()
