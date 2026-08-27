import streamlit as st
import sqlite3
import pandas as pd
import qrcode
from io import BytesIO

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(
    page_title="กิจกรรมที่ 3: AI Persona Simulation Canvas",
    page_icon="🧩",
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
.canvas-card {
    background-color: #FFFFFF !important;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border: 1px solid #E2E8F0;
    border-top: 5px solid #3B82F6;
    color: #1E293B !important;
}
.badge-persona {
    background-color: #EFF6FF !important;
    color: #1D4ED8 !important;
    padding: 3px 10px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 13px;
}
.q-box {
    background-color: #F8FAFC !important;
    border-left: 3px solid #64748B;
    padding: 8px 12px;
    margin: 6px 0;
    border-radius: 0 6px 6px 0;
    font-size: 13.5px;
    color: #1E293B !important;
}
.hmw-box {
    background-color: #FEF3C7 !important;
    border: 1px dashed #D97706;
    padding: 12px;
    border-radius: 8px;
    font-weight: 600;
    color: #92400E !important;
    margin-top: 10px;
    font-size: 13.5px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- 3. ระบบฐานข้อมูล SQLite (รองรับ 100+ คนพร้อมกัน) ---
DB_NAME = "persona_simulation_100users.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=30.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS canvases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT,
                persona_name TEXT,
                q1 TEXT, a1 TEXT,
                q2 TEXT, a2 TEXT,
                q3 TEXT, a3 TEXT,
                pain_points TEXT,
                unmet_needs TEXT,
                how_might_we TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def save_canvas(group_name, persona_name, q1, a1, q2, a2, q3, a3, pain_points, unmet_needs, hmw):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO canvases (
                group_name, persona_name, 
                q1, a1, q2, a2, q3, a3, 
                pain_points, unmet_needs, how_might_we
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (group_name.strip(), persona_name.strip(), q1, a1, q2, a2, q3, a3, pain_points, unmet_needs, hmw))
        conn.commit()

def get_all_canvases():
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM canvases ORDER BY id DESC", conn)
    return df

def clear_db():
    with get_connection() as conn:
        conn.execute("DELETE FROM canvases")
        conn.commit()

init_db()

# --- 4. เมนูด้านข้าง ---
st.sidebar.title("🧩 Activity 3 Control")
view_mode = st.sidebar.radio(
    "เลือกมุมมองหน้าจอ:",
    ["📱 สำหรับผู้เข้าอบรม (บันทึกข้อมูล)", "📊 จอโปรเจกเตอร์วิทยากร (Live Showcase Canvas)"]
)

# ==============================================================================
# 5. หน้าสำหรับผู้เข้าอบรม (Form Submission)
# ==============================================================================
if view_mode == "📱 สำหรับผู้เข้าอบรม (บันทึกข้อมูล)":
    st.markdown("<div class='main-header'>🧩 กิจกรรมที่ 3: AI Persona Simulation</div><div class='sub-header'>โจทย์: Co-thinking with AI (ค้นหา Pain Points และ Unmet Needs ของผู้เรียน)</div>", unsafe_allow_html=True)

    with st.expander("💡 คลิกเพื่อดู 'ตัวอย่างคำสั่ง Prompt สวมบทบาท AI'", expanded=False):
        prompt_example = "จงสวมบทบาทเป็น ด.ช.เอ อายุ 10 ขวบ มีภาวะสมาธิสั้น (ADHD) และรู้สึกเบื่อหน่ายวิชาคณิตศาสตร์ ตอบคำถามสั้นๆ ซื่อๆ ตามความรู้สึกและมุมมองของเด็กประถม"
        st.code(prompt_example, language="text")
        st.caption("👉 คัดลอกข้อความนี้ไปวางใน ChatGPT / Copilot / Gemini แล้วเริ่มสัมภาษณ์ 3 คำถาม")

    if "submitted_act3" not in st.session_state:
        st.session_state.submitted_act3 = False

    if not st.session_state.submitted_act3:
        with st.form("persona_form"):
            st.markdown("#### 1️⃣ ข้อมูลผู้ส่งและ Persona ที่เลือก")
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                group_name = st.text_input("ชื่อผู้จัดทำ / กลุ่มที่ / สาขาวิชา:", placeholder="เช่น นายสมชาย ใจดี หรือ กลุ่ม 1 เอกคอมฯ")
            with col_g2:
                persona_name = st.text_input("Persona ที่สัมภาษณ์:", placeholder="เช่น ด.ช.เอ สมาธิสั้น อายุ 10 ขวบ")

            st.markdown("---")
            st.markdown("#### 2️⃣ บันทึกการสัมภาษณ์ AI (3 คำถามเจาะใจ)")
            
            q1 = st.text_input("คำถามที่ 1 (เช่น ทำไมถึงไม่ชอบเรียนวิชานี้?):", key="q1")
            a1 = st.text_area("คำตอบจาก AI:", height=70, key="a1", placeholder="สรุปคำตอบข้อที่ 1...")

            q2 = st.text_input("คำถามที่ 2 (เช่น ตอนครูสอนรู้สึกอย่างไรบ้าง?):", key="q2")
            a2 = st.text_area("คำตอบจาก AI:", height=70, key="a2", placeholder="สรุปคำตอบข้อที่ 2...")

            q3 = st.text_input("คำถามที่ 3 (เช่น ถ้าเลือกได้ อยากให้ชั่วโมงเรียนเป็นแบบไหน?):", key="q3")
            a3 = st.text_area("คำตอบจาก AI:", height=70, key="a3", placeholder="สรุปคำตอบข้อที่ 3...")

            st.markdown("---")
            st.markdown("#### 3️⃣ สรุปผลลง Problem Statement Canvas")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                pain_points = st.text_area("🔴 ปัญหาหลัก/จุดเจ็บปวด (Pain Points):", height=90, 
                                           placeholder="เช่น นั่งนิ่งฟังบรรยายนานไม่ได้, ตัวเลขเยอะมองไม่เห็นภาพ...")
            with col_p2:
                unmet_needs = st.text_area("🟢 ความต้องการซ่อนเร้น (Unmet Needs):", height=90, 
                                           placeholder="เช่น อยากเรียนแบบได้ขยับร่างกาย, อยากได้โจทย์ที่เชื่อมกับเกม...")

            st.markdown("#### 4️⃣ ตั้งโจทย์ท้าทายนวัตกรรม (How Might We: HMW)")
            hmw = st.text_input("💡 'เราจะช่วย...ได้อย่างไร' (How Might We Question):", 
                                placeholder="เช่น เราจะช่วยให้เด็กสมาธิสั้นเข้าใจเศษส่วนผ่านกิจกรรมเคลื่อนไหวและเกมได้อย่างไร?")

            submit_btn = st.form_submit_button("🚀 ส่งข้อมูล Canvas ขึ้นระบบ", use_container_width=True)

            if submit_btn:
                if not group_name or not hmw or not pain_points:
                    st.error("⚠️ กรุณาระบุชื่อผู้ส่ง/กลุ่ม, Pain Points และข้อความ HMW ให้ครบถ้วนก่อนส่งครับ")
                else:
                    save_canvas(group_name, persona_name, q1, a1, q2, a2, q3, a3, pain_points, unmet_needs, hmw)
                    st.session_state.submitted_act3 = True
                    st.rerun()
    else:
        st.success("🎉 บันทึกผลงาน Problem Statement Canvas เรียบร้อยแล้ว!")
        if st.button("➕ ส่งผลงานเพิ่มเติม / แก้ไข"):
            st.session_state.submitted_act3 = False
            st.rerun()

# ==============================================================================
# 6. หน้าจอโปรเจกเตอร์ / Canva Embed (Live Showcase Canvas Dashboard)
# ==============================================================================
else:
    col_t, col_btn = st.columns([3, 1])
    with col_t:
        st.markdown("<div class='main-header'>📊 Showcase: Problem Statement Canvas</div><div class='sub-header'>รวบรวมโจทย์นวัตกรรมจากการสัมภาษณ์ Persona AI แบบเรียลไทม์</div>", unsafe_allow_html=True)
    with col_btn:
        if st.button("🔄 อัปเดตข้อมูลสด (Refresh)", use_container_width=True):
            st.rerun()

    df = get_all_canvases()

    if df.empty:
        st.warning("⏳ ยังไม่มีผู้ส่ง Canvas... สแกน QR Code ด้านล่างเพื่อเริ่มส่งข้อมูล")
        app_url = st.text_input("ระบุ URL ของ Web App นี้เพื่อสร้าง QR Code:", "http://localhost:8501")
        qr = qrcode.make(app_url)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="สแกนเพื่อร่วมทำกิจกรรมที่ 3", width=220)
    else:
        total_items = len(df)
        m1, m2 = st.columns([1, 3])
        m1.metric("👥 ส่งผลงานแล้ว", f"{total_items} รายการ")

        st.markdown("---")
        
        # ค้นหาและแบ่งหน้าแสดงผล
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            search_query = st.text_input("🔍 ค้นหาชื่อผู้ส่ง / Persona / โจทย์ HMW:", placeholder="พิมพ์ค้นหา...")
        with col_s2:
            items_per_page = st.selectbox("แสดงผลหน้าละ:", [10, 20, 50, 100], index=0)

        filtered_df = df
        if search_query.strip():
            filtered_df = df[
                df["group_name"].str.contains(search_query, case=False, na=False) |
                df["persona_name"].str.contains(search_query, case=False, na=False) |
                df["how_might_we"].str.contains(search_query, case=False, na=False)
            ]

        st.caption(f"แสดง {min(items_per_page, len(filtered_df))} จากทั้งหมด {len(filtered_df)} รายการ")

        # แสดงการ์ด 2 คอลัมน์ (โครงสร้างชิดซ้ายไม่มี Indent เพื่อป้องกันปัญหา Markdown Code Block)
        cols = st.columns(2)
        for idx, row in filtered_df.head(items_per_page).reset_index().iterrows():
            col_target = cols[idx % 2]
            with col_target:
                q1_c = str(row['q1']).replace('\n', '<br>')
                a1_c = str(row['a1']).replace('\n', '<br>')
                q2_c = str(row['q2']).replace('\n', '<br>')
                a2_c = str(row['a2']).replace('\n', '<br>')
                q3_c = str(row['q3']).replace('\n', '<br>')
                a3_c = str(row['a3']).replace('\n', '<br>')
                pain_c = str(row['pain_points']).replace('\n', '<br>')
                unmet_c = str(row['unmet_needs']).replace('\n', '<br>')
                hmw_c = str(row['how_might_we']).replace('\n', '<br>')

                card_html = (
                    f"<div class='canvas-card'>"
                    f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>"
                    f"<span style='font-size:16px;font-weight:bold;color:#1E40AF;'>🏆 {row['group_name']}</span>"
                    f"<span class='badge-persona'>👤 {row['persona_name']}</span>"
                    f"</div>"
                    f"<div style='margin-bottom:10px;'>"
                    f"<b>💬 ผลการสัมภาษณ์ 3 คำถาม:</b>"
                    f"<div class='q-box'><b>Q1:</b> {q1_c}<br><b>A1:</b> {a1_c}</div>"
                    f"<div class='q-box'><b>Q2:</b> {q2_c}<br><b>A2:</b> {a2_c}</div>"
                    f"<div class='q-box'><b>Q3:</b> {q3_c}<br><b>A3:</b> {a3_c}</div>"
                    f"</div>"
                    f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:13px;margin-bottom:8px;'>"
                    f"<div style='background-color:#FEF2F2;padding:8px;border-radius:6px;border-left:3px solid #EF4444;color:#1E293B;'>"
                    f"<b style='color:#991B1B;'>🔴 Pain Points:</b><br>{pain_c}"
                    f"</div>"
                    f"<div style='background-color:#F0FDF4;padding:8px;border-radius:6px;border-left:3px solid #22C55E;color:#1E293B;'>"
                    f"<b style='color:#166534;'>🟢 Unmet Needs:</b><br>{unmet_c}"
                    f"</div>"
                    f"</div>"
                    f"<div class='hmw-box'>💡 <b>How Might We (โจทย์นวัตกรรม):</b><br>{hmw_c}</div>"
                    f"</div>"
                )
                st.markdown(card_html, unsafe_allow_html=True)

        st.markdown("---")
        with st.expander("⚙️ เครื่องมือจัดการข้อมูลและดาวน์โหลด (สำหรับวิทยากร)"):
            st.dataframe(df)
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลดข้อมูล Canvas ทั้งหมดเป็น CSV (Excel ภาษาไทย)",
                data=csv_data,
                file_name="activity3_persona_canvas_results.csv",
                mime="text/csv"
            )
            if st.button("🗑️ ล้างข้อมูลทั้งหมดเพื่อเริ่มรอบใหม่", type="primary"):
                clear_db()
                st.rerun()
