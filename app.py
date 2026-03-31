import streamlit as st
import random
import datetime
import google.generativeai as genai

# --- 1. 頁面配置 ---
st.set_page_config(
    page_title="天機啟示錄 | 數位祭壇",
    page_icon="☯️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS 樣式 (保持你的黑金視覺) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700&display=swap');
    .stApp { background: radial-gradient(circle at top right, #1a1a1a, #000000); color: #e0e0e0; font-family: 'Noto Serif TC', serif; }
    .gua-line { font-family: monospace; font-size: 45px; line-height: 1.2; text-shadow: 0 0 15px rgba(255,255,255,0.2); }
    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
    .moving-yao { animation: blink 1.5s infinite; color: #f1c40f !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. 讀取 API KEY (關鍵修復) ---
# 優先讀取 Streamlit Secrets，如果沒有才看 sidebar
api_key = st.secrets.get("GEMINI_API_KEY")

# --- 4. 核心邏輯 ---
class IChingApp:
    def __init__(self):
        self.bagua = {"111":"乾","000":"坤","100":"震","011":"巽","010":"坎","101":"離","001":"艮","110":"兌"}
    def cast(self): return [sum([random.choice([2,3]) for _ in range(3)]) for _ in range(6)]
    def get_name(self, bin_str):
        up, down = self.bagua[bin_str[3:]], self.bagua[bin_str[:3]]
        db = {"110100":"風山漸","111111":"乾為天","000000":"坤為地","101101":"離為火"}
        return db.get(bin_str, f"{up}{down}卦")

# --- 5. 主程式 ---
def main():
    st.markdown('<div style="text-align:center;"><h1 style="color:#f1c40f; letter-spacing:10px;">☯ 天機啟示錄</h1><p style="color:#666;">DIGITAL DIVINATION TERMINAL v4.1</p></div>', unsafe_allow_html=True)

    # 檢查 API KEY 是否存在
    if not api_key:
        with st.sidebar:
            st.error("❌ 未偵測到 Secrets 中的 GEMINI_API_KEY")
            temp_key = st.text_input("請手動輸入 API Key", type="password")
            if temp_key:
                st.session_state['api_key'] = temp_key
        
        # 如果 sidebar 有輸入就用 sidebar 的
        final_key = st.session_state.get('api_key')
    else:
        final_key = api_key
        st.sidebar.success("✅ 已從後台 Secrets 成功載入金鑰")

    # 輸入區
    question = st.text_input("🤔 請問您想請教何事？", placeholder="例如：今日財運...")

    if st.button("🔮 撥開雲霧，啟動占卜", use_container_width=True):
        if not final_key:
            st.warning("⚠️ 系統遺失金鑰，請檢查 Streamlit Cloud 的 Secrets 設定。")
            return
        
        app = IChingApp()
        scores = app.cast()
        orig_bin = "".join(["1" if s in [7, 9] else "0" for s in scores])
        chan_bin = "".join([("0" if s == 9 else "1" if s == 6 else "1" if s == 7 else "0") for s in scores])
        orig_name = app.get_name(orig_bin)
        chan_name = app.get_name(chan_bin)
        
        # 配置 AI
        genai.configure(api_key=final_key)
        # 修正：目前 Streamlit 環境建議使用 stable 版本或最新預覽版
        model = genai.GenerativeModel('gemini-1.5-flash') 
        
        with st.spinner("正在讀取 2026 時空能量..."):
            try:
                prompt = f"你是易經大師。問題：{question}。本卦：{orig_name}，變卦：{chan_name}。請以 HTML 格式進行簡短精闢的解析。"
                response = model.generate_content(prompt)
                ai_text = response.text
                
                # 顯示結果
                col_gua, col_ai = st.columns([1, 2])
                with col_gua:
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05); padding:30px; border-radius:20px; text-align:center; border:1px solid rgba(241,196,15,0.3);">
                        <h2 style="color:#f1c40f;">{orig_name}</h2>
                        {"".join([f"<div class='gua-line' style='color:{('#ff4d4d' if s in [7,9] else '#00d2ff')};'>{'━━━━━━' if s in [7,9] else '━━━&nbsp;&nbsp;&nbsp;━━━'}{' <span class=\"moving-yao\">★</span>' if s in [6,9] else ''}</div>" for s in reversed(scores)])}
                        <p style="font-size:12px; color:#888; margin-top:20px;">趨向：{chan_name}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col_ai:
                    st.markdown(f"<div style='background:rgba(0,0,0,0.3); padding:30px; border-radius:20px; border-left:5px solid #f1c40f;'>{ai_text}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"AI 運算錯誤：{str(e)}")

if __name__ == "__main__":
    main()
