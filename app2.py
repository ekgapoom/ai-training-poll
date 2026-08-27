import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import qrcode
from io import BytesIO
import textwrap

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(
    page_title="กิจกรรมที่ 2: วิเคราะห์กรณีศึกษา Pedagogy Leads, AI Follows",
    page_icon="⚖️",
    layout="wide"
)

# --- 2. ปรับแต่ง CSS ---
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
        background-color: #FEF2F2;
        border-radius: 10px;
        padding: 14px;
        border: 1px solid #FECACA;
        border-left: 4px solid #EF4444;
        font-size: 14px;
        margin-bottom: 12px;
    }
    .case-card-pedagogy {
        background-color: #F0FDF4;
        border-radius: 10px;
        padding: 14px;
        border: 1px solid #BBF7D0;
        border-left: 4px solid #22C55E;
        font-size: 14px;
        margin-bottom: 12px;
    }
    .analysis-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #E2E8F0;
        border-top: 5px solid #6366F1;
    }
    .badge-bias {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin-right: 4px;
        margin-bottom: 4px;
    }
    .must-define-box {
        background-color: #F0F9FF;
        border-left: 3px solid #0284C7;
        padding: 10px 12px;
        border-radius: 0 8px 8px 0;
        font-size: 13.5px;
        margin-top: 10px;
        color: #0C4A6E;
    }
</style>
""")
st.markdown(custom_css, unsafe_allow_html=True)

# --- 3. ระบบฐานข้อมูล SQLite ---
DB_NAME = "case_study_act2.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS case_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT,
            bias_dimensions TEXT,
            weaknesses TEXT,
            must_define_first TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_analysis(group_name, bias_dimensions, weaknesses, must_define_first):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO case_analyses (group_name, bias_dimensions, weaknesses, must_define_first)
        VALUES (?, ?, ?, ?)
    """, (group_name.strip(), ", ".join(bias_dimensions), weaknesses.strip(), must_define_first.strip()))
    conn.commit()
    conn.close()

def get_all_analyses():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM case_analyses ORDER BY id DESC", conn)
    conn.close()
    return df

def clear_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM case_analyses")
    conn.commit()
    conn.close()

init_db()

# --- 4. เมนูด้านข้าง (Navigation) ---
st.sidebar.title("⚖️ Activity 2 Control")
view_mode = st.sidebar.radio(
    "เลือกหน้าจอแสดงผล:",
    ["📱 สำหรับผู้เข้าอบรม (วิเคราะห์กรณีศึกษา)", "📊 จอโปรเจกเตอร์ (Live Insights Dashboard)"]
)

# ==============================================================================
# 5. หน้าสำหรับผู้เข้าอบรม (Student Submission)
# ==============================================================================
if view_mode == "📱 สำหรับผู้เข้าอบรม (วิเคราะห์กรณีศึกษา)":
    header_html = textwrap.dedent("""
    <div class='main-header'>⚖️ กิจกรรมที่ 2: วิเคราะห์กรณีศึกษา (Case Study)</div>
    <div class='sub-header'>"Pedagogy Leads, AI Follows" (ศาสตร์การสอนต้องนำ เทคโนโลยีต้องตาม)</div>
    """)
    st.markdown(header_html, unsafe_allow_html=True)

    # กล่องสรุปกรณีศึกษาเทียบกัน
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        case1_html = textwrap.dedent("""
        <div class='case-card-ai'>
            <b>📕 แผนที่ 1: AI-Driven (ให้ AI คิดแทน 100%)</b><br>
            ใช้ Prompt กว้างๆ AI สร้างแผนการสอนที่สมบูรณ์แบบตามทฤษฎี แต่ใช้อุปกรณ์ที่โรงเรียนไม่มี และไม่เข้ากับบริบทเด็กในพื้นที่
        </div>
        """)
        st.markdown(case1_html, unsafe_allow_html=True)
    with col_c2:
        case2_html = textwrap.dedent("""
        <div class='case-card-pedagogy'>
            <b>📗 แผนที่ 2: Pedagogy-Driven (ครูนำ AI ตาม)</b><br>
            ครูกำหนดเป้าหมายและข้อจำกัดก่อน (Pedagogy) แล้วใช้ AI ช่วยคิดเกมและการประเมินผลที่สอดคล้องกับเด็กในชุมชน
        </div>
        """)
        st.markdown(case2_html, unsafe_allow_html=True)

    if "submitted_act2" not in st.session_state:
        st.session_state.submitted_act2 = False

    if not st.session_state.submitted_act2:
        with st.form("case_form"):
            group_name = st.text_input("กลุ่มที่ / ชื่อกลุ่ม (เช่น กลุ่ม 3 เอกภาษาอังกฤษ):", placeholder="ระบุชื่อกลุ่ม...")
            
            st.markdown("---")
            st.markdown("#### 🔍 ชวนคิด: ท่านคิดว่าแผนที่ 1 มีจุดบอดและอคติ (Bias) ในมิติใดบ้าง?")
            bias_options = [
                "💻 บริบทความพร้อมด้านอุปกรณ์และโครงสร้างพื้นฐาน (Digital Divide)",
                "🌾 ความสอดคล้องกับบริบทชุมชนและวัฒนธรรมท้องถิ่น (Cultural/Context Bias)",
                "🎯 ความเข้าใจความต้องการจริงของเด็ก (Lack of Empathy)",
                "⏱️ ความเป็นไปได้ในการจัดการเรียนรู้จริงในห้องเรียน (Practical Feasibility)",
                "📖 การยึดติดกับทฤษฎีฝรั่งมากเกินไปโดยไม่ปรับบริบท (Western Model Bias)"
            ]
            selected_biases = st.multiselect(
                "เลือกมิติจุดบอด/อคติที่กลุ่มท่านพบ (เลือกได้มากกว่า 1 ข้อ):",
                options=bias_options
            )

            weaknesses = st.text_area(
                "💬 อธิบายเจาะลึกจุดบอดของแผนที่ 1:",
                placeholder="เช่น การให้ AI คิดโดยไม่มีขอบเขต ทำให้ได้กิจกรรมหรูหราที่ใช้ Smart Board และ VR แต่เด็กโรงเรียนชนบทเข้าไม่ถึง..."
            )

            st.markdown("---")
            st.markdown("#### 💡 บทเรียนสำหรับครูนวัตกร")
            must_define = st.text_area(
                "🔑 สิ่งที่ครู 'ต้องกำหนดให้ชัดเจนก่อนสั่งการ AI' คืออะไร?",
                placeholder="เช่น กำหนดวัตถุประสงค์การเรียนรู้ (KPA), บริบทความพร้อมของสื่อในห้อง, และระดับพัฒนาการของเด็ก..."
            )

            submit_btn = st.form_submit_button("🚀 ส่งผลการวิเคราะห์ขึ้นจอโปรเจกเตอร์", use_container_width=True)

            if submit_btn:
                if not group_name or not selected_biases or not weaknesses or not must_define:
                    st.error("⚠️ กรุณากรอกข้อมูลให้ครบถ้วนทุกช่องก่อนกดส่งครับ")
                else:
                    save_analysis(group_name, selected_biases, weaknesses, must_define)
                    st.session_state.submitted_act2 = True
                    st.rerun()
    else:
        st.success("🎉 บันทึกผลการวิเคราะห์เรียบร้อยแล้ว! ข้อมูลถูกส่งไปยังจอแสดงผลแล้วครับ")
        if st.button("➕ ส่งผลการวิเคราะห์เพิ่มเติม / แก้ไข"):
            st.session_state.submitted_act2 = False
            st.rerun()

# ==============================================================================
# 6. หน้าจอโปรเจกเตอร์ / Canva Embed (Live Insights Dashboard)
# ==============================================================================
else:
    col_t, col_btn = st.columns([3, 1])
    with col_t:
        dash_header = textwrap.dedent("""
        <div class='main-header'>📊 Live Insights: เจาะลึกจุดบอด "AI-Driven vs Pedagogy-Driven"</div>
        <div class='sub-header'>ภาพรวมมุมมองของว่าที่ครูนวัตกรต่อการใช้ AI อย่างมีวิจารณญาณ</div>
        """)
        st.markdown(dash_header, unsafe_allow_html=True)
    with col_btn:
        if st.button("🔄 อัปเดตข้อมูลสด (Refresh)", use_container_width=True):
            st.rerun()

    df = get_all_analyses()

    if df.empty:
        st.warning("⏳ ยังไม่มีกลุ่มใดส่งบทวิเคราะห์... สแกน QR Code ด้านล่างเพื่อเริ่มกิจกรรม")
        app_url = st.text_input("ระบุ URL ของแอปนี้เพื่อสร้าง QR Code:", "http://localhost:8501")
        qr = qrcode.make(app_url)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="สแกนเพื่อร่วมวิเคราะห์กรณีศึกษา", width=220)
    else:
        # สถิติภาพรวม
        st.info(f"👥 ส่งผลการวิเคราะห์แล้วทั้งหมด **{len(df)}** กลุ่ม")

        # ประมวลผลมิติจุดบอด (Bias Dimension Frequencies)
        all_biases = []
        for b_str in df["bias_dimensions"].dropna():
            all_biases.extend([b.strip() for b in b_str.split(",") if b.strip()])
        
        bias_df = pd.Series(all_biases).value_counts().reset_index()
        bias_df.columns = ["มิติจุดบอด/อคติ", "จำนวนกลุ่มที่โหวต"]

        # จัด Layout: กราฟแท่งสรุปสถิติ
        fig_bar = px.bar(
            bias_df,
            x="จำนวนกลุ่มที่โหวต",
            y="มิติจุดบอด/อคติ",
            orientation="h",
            title="📊 มิติจุดบอดและอคติ (Bias) ที่ถูกค้นพบมากที่สุด",
            color="จำนวนกลุ่มที่โหวต",
            color_continuous_scale="Reds"
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=280, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        st.markdown("### 💬 รวมมุมมองและการถอดบทเรียนรายกลุ่ม")

        # แสดงการ์ดวิเคราะห์รายกลุ่ม 2 คอลัมน์
        cols = st.columns(2)
        for idx, row in df.iterrows():
            col_target = cols[idx % 2]
            with col_target:
                # สร้าง Badge สำหรับแต่ละ Bias
                badges_html = "".join([f"<span class='badge-bias'>⚠️ {b.strip()}</span>" for b in row['bias_dimensions'].split(",") if b.strip()])
                
                card_html = textwrap.dedent(f"""
                <div class='analysis-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                        <span style='font-size: 17px; font-weight: bold; color: #1E3A8A;'>🏆 {row['group_name']}</span>
                    </div>
                    <div style='margin-bottom: 8px;'>{badges_html}</div>
                    
                    <div style='font-size: 13.5px; color: #374151; margin-bottom: 8px;'>
                        <b>🔍 จุดบอดของแผนที่ 1:</b><br>{row['weaknesses']}
                    </div>
                    
                    <div class='must-define-box'>
                        <b>🔑 สิ่งที่ครูต้องกำหนดก่อนใช้ AI:</b><br>{row['must_define_first']}
                    </div>
                </div>
                """)
                st.markdown(card_html, unsafe_allow_html=True)

        # เมนูสำหรับวิทยากรดาวน์โหลด
        st.markdown("---")
        with st.expander("⚙️ เครื่องมือจัดการข้อมูลและดาวน์โหลด (สำหรับวิทยากร)"):
            st.dataframe(df)
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลดผลวิเคราะห์เป็น CSV (Excel ภาษาไทย)",
                data=csv_data,
                file_name="activity2_case_analysis.csv",
                mime="text/csv"
            )
            if st.button("🗑️ ล้างข้อมูลทั้งหมดเพื่อเริ่มรอบใหม่", type="primary"):
                clear_db()
                st.rerun()
