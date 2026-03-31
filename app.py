import streamlit as st
import random
import datetime
import google.generativeai as genai

# --- 1. 頁面配置 ---
st.set_page_config(
    page_title="天機啟示錄 | 數位祭壇",
    page_icon="☯️",
    layout="wide", # 強制寬螢幕比例
    initial_sidebar_state="collapsed"
)

# --- 2. CSS 樣式注入 (保留你的黑金琉璃視覺) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700&display=swap');
    
    /* 隱藏 Streamlit 預設元件 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background: radial-gradient(circle at top right, #1a1a1a, #000000);
        color: #e0e0e0;
        font-family: 'Noto Serif TC', serif;
    }
    
    .main-container {
        background: rgba(255, 255, 255, 0.02);
        padding: 40px;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 40px 100px rgba(0,0,0,0.8);
        margin-top: 20px;
    }

    .gua-line {
        font-family: monospace;
        font-size: 45px;
        line-height: 1.2;
        text-shadow: 0 0 15px rgba(255,255,255,0.2);
    }
    
    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
    .moving-yao { animation: blink 1.5s infinite; color: #f1c40f !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. 核心邏輯 ---
def get_iching_context():
    vitality = {"木": 98, "火": 75, "土": 35, "金": 40, "水": 25}
    return {"year": "丙午年", "month": "辛卯月", "energy": vitality}

class IChingApp:
    def __init__(self):
        self.bagua = {
            "111": "乾", "000": "坤", "100": "震", "011": "巽",
            "010": "坎", "101": "離", "001": "艮", "110": "兌"
        }

    def cast(self):
        return [sum([random.choice([2, 3]) for _ in range(3)]) for _ in range(6)]

    def get_name(self, bin_str):
        up, down = self.bagua[bin_str[3:]], self.bagua[bin_str[:3]]
        db = {"110100": "風山漸", "111111": "乾為天", "000000": "坤為地", "101101": "離為火"}
        return db.get(bin_str, f"{up}{down}卦")

# --- 4. Streamlit UI 介面 ---
def main():
    st.markdown('<div style="text-align:center;"><h1 style="color:#f1c40f; letter-spacing:10px;">☯ 天機啟示錄</h1><p style="color:#666;">DIGITAL DIVINATION TERMINAL v4.0</p></div>', unsafe_allow_html=True)
    
    # 側邊欄配置 API Key
    with st.sidebar:
        st.title("⚙️ 系統設置")
        api_key = st.text_input("輸入 Gemini API Key", type="password")
        st.info("2026 丙午年 · 仲春氣場偵測中...")

    # 主輸入區
    col_input, col_energy = st.columns([3, 1])
    with col_input:
        question = st.text_input("🤔 請問您想請教何事？", placeholder="例如：今日財運、事業展望...")
    
    with col_energy:
        ctx = get_iching_context()
        for el, val in ctx['energy'].items():
            st.caption(f"{el}氣: {val}%")
            st.progress(val/100)

    if st.button("🔮 撥開雲霧，啟動占卜", use_container_width=True):
        if not api_key:
            st.error("請先在側邊欄填入 API Key！")
            return
        
        app = IChingApp()
        scores = app.cast()
        orig_bin = "".join(["1" if s in [7, 9] else "0" for s in scores])
        chan_bin = "".join([("0" if s == 9 else "1" if s == 6 else "1" if s == 7 else "0") for s in scores])
        
        orig_name = app.get_name(orig_bin)
        chan_name = app.get_name(chan_bin)
        
        # 呼叫 AI
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash') # 或 gemini-3-flash
        
        with st.spinner("正在讀取 2026 時空能量..."):
            prompt = f"問題：{question}。本卦：{orig_name}，變卦：{chan_name}。請以大師口吻進行解析，使用繁體中文 HTML 格式。"
            response = model.generate_content(prompt)
            ai_text = response.text

        # 展示結果
        col_gua, col_ai = st.columns([1, 2])
        
        with col_gua:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05); padding:30px; border-radius:20px; text-align:center; border:1px solid rgba(241,196,15,0.3);">
                <h2 style="color:#f1c40f;">{orig_name}</h2>
                <div style="margin:20px 0;">
                {"".join([f"<div class='gua-line' style='color:{('#ff4d4d' if s in [7,9] else '#00d2ff')};'>{'━━━━━━' if s in [7,9] else '━━━&nbsp;&nbsp;&nbsp;━━━'}{' <span class=\"moving-yao\">★</span>' if s in [6,9] else ''}</div>" for s in reversed(scores)])}
                </div>
                <p style="font-size:12px; color:#888;">趨向：{chan_name}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_ai:
            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.3); padding:30px; border-radius:20px; border-left:5px solid #f1c40f; min-height:400px;">
                <div style="color:#d1d8e0; line-height:1.8;">{ai_text}</div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
