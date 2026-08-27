import streamlit as st
import sqlite3
import pandas as pd
import qrcode
from io import BytesIO

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(
    page_title="กิจกรรมที่ 3: AI Persona Simulation Canvas",
    page_icon="🧩",
    layout="wide"
)

# --- ตกแต่ง CSS ให้สวยงาม เหมาะกับการแสดงผลทั้งมือถือและโปรเจกเตอร์ ---
st.markdown("""
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
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-top: 5px solid #3B82F6;
    }
    .badge {
        background-color: #EFF6FF;
        color: #1D4ED8;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 13px;
        display: inline-block;
    }
    .q-box {
        background-color: #F8FAFC;
        border-left: 3px solid #64748B;
        padding: 8px 12px;
        margin: 6px 0;
        border-radius: 0 6px 6px 0;
        font-size: 14px;
    }
    .hmw-box {
        background-color: #FEF3C7;
        border: 1px dashed #D97706;
        padding: 12px;
        border-radius: 8px;
        font-weight: 600;
        color: #92400E;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- ระบบฐานข้อมูล SQLite ---
DB_NAME = "persona_simulation.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
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
    conn.close()

def save_canvas(group_name, persona_name, q1, a1, q2, a2, q3, a3, pain_points, unmet_needs, hmw):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO canvases (
            group_name, persona_name, 
            q1, a1, q2, a2, q3, a3, 
            pain_points, unmet_needs, how_might_we
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (group_name.strip(), persona_name.strip(), q1, a1, q2, a2, q3, a3, pain_points, unmet_needs, hmw))
    conn.commit()
    conn.close()

def get_all_canvases():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM canvases ORDER BY id DESC", conn)
    conn.close()
    return df

def clear_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM canvases")
    conn.commit()
    conn.close()

init_db()

# --- เมนูด้านข้าง (Navigation) ---
st.sidebar.title("🧩 Activity 3 Control")
view_mode = st.sidebar.radio(
    "เลือกหน้าจอแสดงผล:",
    ["📱 สำหรับผู้เข้าอบรม (บันทึกข้อมูล)", "📊 จอโปรเจกเตอร์ (Live Showcase Canvas)"]
)

# ==============================================================================
# 1. หน้านักศึกษา (Student Form Submission)
# ==============================================================================
if view_mode == "📱 สำหรับผู้เข้าอบรม (บันทึกข้อมูล)":
    st.markdown("<div class='main-header'>🧩 กิจกรรมที่ 3: AI Persona Simulation</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>โจทย์: Co-thinking with AI (ค้นหา Pain Points และ Unmet Needs ของผู้เรียน)</div>", unsafe_allow_html=True)

    # กล่องแนะนำ Prompt จำลอง Persona
    with st.expander("💡 คลิกเพื่อคัดลอก 'ตัวอย่างคำสั่ง Prompt สวมบทบาท AI'", expanded=False):
        prompt_example = "จงสวมบทบาทเป็น ด.ช.เอ อายุ 10 ขวบ มีภาวะสมาธิสั้น (ADHD) และรู้สึกเบื่อหน่ายวิชาคณิตศาสตร์ ตอบคำถามสั้นๆ ซื่อๆ ตามความรู้สึกและมุมมองของเด็กประถม"
        st.code(prompt_example, language="text")
        st.caption("👉 คัดลอกข้อความนี้ไปวางใน ChatGPT / Copilot / Gemini แล้วเริ่มสัมภาษณ์ 3 คำถาม")

    if "submitted_act3" not in st.session_state:
        st.session_state.submitted_act3 = False

    if not st.session_state.submitted_act3:
        with st.form("persona_form"):
            st.markdown("#### 1️⃣ ข้อมูลกลุ่มและ Persona ที่เลือก")
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                group_name = st.text_input("กลุ่มที่ / ชื่อกลุ่ม (เช่น กลุ่ม 1 สาขาคณิตศาสตร์):", placeholder="ระบุชื่อกลุ่ม...")
            with col_g2:
                persona_name = st.text_input("Persona ที่สัมภาษณ์ (เช่น ด.ช.เอ สมาธิสั้น อายุ 10 ขวบ):", placeholder="ระบุลักษณะ Persona...")

            st.markdown("---")
            st.markdown("#### 2️⃣ บันทึกการสัมภาษณ์ AI (3 คำถามเจาะใจ)")
            
            st.markdown("**คำถามที่ 1:**")
            q1 = st.text_input("คำถามที่ 1 (เช่น ทำไมถึงไม่ชอบเรียนคณิตศาสตร์?):", key="q1")
            a1 = st.text_area("คำตอบจาก AI:", height=70, key="a1", placeholder="สรุปใจความสำคัญของคำตอบ...")

            st.markdown("**คำถามที่ 2:**")
            q2 = st.text_input("คำถามที่ 2 (เช่น ตอนครูสอนรู้สึกอย่างไรบ้าง?):", key="q2")
            a2 = st.text_area("คำตอบจาก AI:", height=70, key="a2", placeholder="สรุปใจความสำคัญของคำตอบ...")

            st.markdown("**คำถามที่ 3 (เจาะลึกความต้องการ):**")
            q3 = st.text_input("คำถามที่ 3 (เช่น ถ้าเลือกได้ อยากให้ชั่วโมงเรียนเป็นแบบไหน?):", key="q3")
            a3 = st.text_area("คำตอบจาก AI:", height=70, key="a3", placeholder="สรุปใจความสำคัญของคำตอบ...")

            st.markdown("---")
            st.markdown("#### 3️⃣ สรุปผลลง Problem Statement Canvas")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                pain_points = st.text_area("🔴 ปัญหาหลัก/จุดเจ็บปวด (Pain Points):", height=90, 
                                           placeholder="เช่น นั่งนิ่งๆ ฟังบรรยายนานไม่ได้, ตัวเลขเยอะตาลายและมองไม่เห็นภาพ...")
            with col_p2:
                unmet_needs = st.text_area("🟢 ความต้องการซ่อนเร้น (Unmet Needs):", height=90, 
                                           placeholder="เช่น อยากได้เรียนแบบได้ขยับร่างกาย, อยากได้โจทย์ที่เชื่อมกับเกมที่เล่น...")

            st.markdown("#### 4️⃣ ตั้งโจทย์ท้าทายนวัตกรรม (How Might We: HMW)")
            hmw = st.text_input("💡 'เราจะช่วย...ได้อย่างไร' (How Might We Question):", 
                                placeholder="เช่น เราจะช่วยให้เด็กสมาธิสั้นเข้าใจเศษส่วนผ่านกิจกรรมขยับร่างกายและเกมได้อย่างไร?")

            submit_btn = st.form_submit_button("🚀 ส่งข้อมูล Canvas ขึ้นจอโปรเจกเตอร์", use_container_width=True)

            if submit_btn:
                if not group_name or not hmw or not pain_points:
                    st.error("⚠️ กรุณาระบุชื่อกลุ่ม, Pain Points และข้อความ HMW ให้ครบถ้วนก่อนส่งครับ")
                else:
                    save_canvas(group_name, persona_name, q1, a1, q2, a2, q3, a3, pain_points, unmet_needs, hmw)
                    st.session_state.submitted_act3 = True
                    st.rerun()
    else:
        st.success("🎉 บันทึกผลงาน Problem Statement Canvas เรียบร้อยแล้ว! ข้อมูลถูกส่งขึ้นจอวิทยากรแล้วครับ")
        if st.button("➕ ส่งผลงานเพิ่มเติม / แก้ไข"):
            st.session_state.submitted_act3 = False
            st.rerun()

# ==============================================================================
# 2. หน้าจอโปรเจกเตอร์ / Canva Embed (Live Showcase Canvas Dashboard)
# ==============================================================================
else:
    col_t, col_btn = st.columns([3, 1])
    with col_t:
        st.markdown("<div class='main-header'>📊 Showcase: Problem Statement Canvas</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-header'>รวบรวมโจทย์นวัตกรรมจากการสัมภาษณ์ Persona AI ของทุกกลุ่ม</div>", unsafe_allow_html=True)
    with col_btn:
        if st.button("🔄 อัปเดตข้อมูลสด (Refresh)", use_container_width=True):
            st.rerun()

    df = get_all_canvases()

    if df.empty:
        st.warning("⏳ ยังไม่มีกลุ่มใดส่ง Canvas... สามารถสแกน QR Code ด้านล่างเพื่อเริ่มส่งข้อมูล")
        
        # ส่วนแสดง QR Code สำหรับสแกนเข้าหน้าบันทึก
        app_url = st.text_input("ระบุ URL ของ Web App นี้เพื่อสร้าง QR Code:", "http://localhost:8501")
        qr = qrcode.make(app_url)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="สแกนเพื่อเข้าทำกิจกรรมที่ 3", width=240)
    else:
        st.info(f"🎉 มีกลุ่มส่งผลงานแล้วทั้งหมด **{len(df)}** กลุ่ม")
        st.markdown("---")

        # แสดงผล Canvas การ์ดแบบ 2 คอลัมน์บนจอโปรเจกเตอร์
        cols = st.columns(2)
        for idx, row in df.iterrows():
            col_target = cols[idx % 2]
            with col_target:
                st.markdown(f"""
                <div class='canvas-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                        <span style='font-size: 18px; font-weight: bold; color: #1E40AF;'>🏆 {row['group_name']}</span>
                        <span class='badge'>👤 {row['persona_name']}</span>
                    </div>
                    
                    <div style='margin-bottom: 10px;'>
                        <b>💬 การสัมภาษณ์ 3 คำถาม:</b>
                        <div class='q-box'><b>Q1:</b> {row['q1']}<br><b>A1:</b> {row['a1']}</div>
                        <div class='q-box'><b>Q2:</b> {row['q2']}<br><b>A2:</b> {row['a2']}</div>
                        <div class='q-box'><b>Q3:</b> {row['q3']}<br><b>A3:</b> {row['a3']}</div>
                    </div>
                    
                    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;'>
                        <div style='background-color: #FEF2F2; padding: 8px; border-radius: 6px; border-left: 3px solid #EF4444;'>
                            <b style='color: #991B1B;'>🔴 Pain Points:</b><br>{row['pain_points']}
                        </div>
                        <div style='background-color: #F0FDF4; padding: 8px; border-radius: 6px; border-left: 3px solid #22C55E;'>
                            <b style='color: #166534;'>🟢 Unmet Needs:</b><br>{row['unmet_needs']}
                        </div>
                    </div>
                    
                    <div class='hmw-box'>
                        💡 <b>How Might We (โจทย์นวัตกรรม):</b><br>{row['how_might_we']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # จัดการข้อมูลด้านล่าง (Export & Clear)
        st.markdown("---")
        with st.expander("⚙️ เครื่องมือจัดการข้อมูลและดาวน์โหลด (สำหรับวิทยากร)"):
            st.dataframe(df)
            
            # ปุ่ม Export เป็น CSV
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลดข้อมูลทั้งหมดเป็น CSV (Excel รองรับภาษาไทย)",
                data=csv_data,
                file_name="activity3_persona_canvas.csv",
                mime="text/csv"
            )
            
            if st.button("🗑️ ล้างข้อมูลทั้งหมดเพื่อเริ่มกลุ่มใหม่", type="primary"):
                clear_db()
                st.rerun()