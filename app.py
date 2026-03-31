import streamlit as st
import random
import google.generativeai as genai
from google.api_core import exceptions

# --- 1. 頁面配置 ---
st.set_page_config(page_title="天機啟示錄 | 2026 數位祭壇", layout="wide")

# --- 2. CSS 視覺 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700&display=swap');
    .stApp { background-color: #fcfcfc; color: #2d3436; font-family: 'Noto Serif TC', serif; }
    .main-title { text-align: center; color: #2d3436; letter-spacing: 10px; font-weight: 700; margin-top: 20px; }
    .glass-card { background: #ffffff; padding: 30px; border-radius: 20px; border: 1px solid #eee; box-shadow: 0 10px 40px rgba(0,0,0,0.03); margin-bottom: 20px; }
    .gua-line { font-family: monospace; font-size: 50px; line-height: 1.1; text-align: center; margin: 5px 0; }
    .stButton>button { background-color: #2d3436; color: white; border-radius: 12px; border: none; padding: 12px; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #f1c40f; color: #000; }
</style>
""", unsafe_allow_html=True)

# --- 3. 占卜邏輯 ---
def cast_iching():
    scores = [sum([random.choice([2, 3]) for _ in range(3)]) for _ in range(6)]
    bagua = {"111":"乾","000":"坤","100":"震","011":"巽","010":"坎","101":"離","001":"艮","110":"兌"}
    bin_str = "".join(["1" if s in [7, 9] else "0" for s in scores])
    up, down = bagua[bin_str[3:]], bagua[bin_str[:3]]
    names = {"111111":"乾為天", "000000":"坤為地", "110100":"風山漸", "101101":"離為火", "010010":"坎為水"}
    full_name = names.get(bin_str, f"{up}{down}卦")
    chan_bin = "".join([("0" if s == 9 else "1" if s == 6 else "1" if s == 7 else "0") for s in scores])
    chan_name = names.get(chan_bin, f"{bagua[chan_bin[3:]]}{bagua[chan_bin[:3]]}卦")
    return scores, full_name, chan_name

# --- 4. 主程式 ---
def main():
    st.markdown('<h1 class="main-title">☯ 天機啟示錄</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#bdc3c7; margin-bottom:40px;">2026 DIGITAL ALTAR v5.0</p>', unsafe_allow_html=True)

    api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("輸入 API Key", type="password")

    question = st.text_input("🔮 欲請教天機之事：", placeholder="請輸入疑惑...")
    
    if st.button("啟動占卜儀式"):
        if not api_key:
            st.warning("⚠️ 系統未偵測到金鑰。")
            return

        scores, gua_name, chan_name = cast_iching()
        genai.configure(api_key=api_key)

        col_l, col_r = st.columns([1, 1.5], gap="large")
        
        with col_l:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;">
                <h2 style="color:#2d3436;">{gua_name}</h2>
                <div style="margin:25px 0;">
                {"".join([f"<div class='gua-line' style='color:{('#d63031' if s in [7,9] else '#2d3436')};'>{'━━━━━━' if s in [7,9] else '━━━&nbsp;&nbsp;&nbsp;━━━'}{' <span style=\"color:#f1c40f; font-size:24px;\">●</span>' if s in [6,9] else ''}</div>" for s in reversed(scores)])}
                </div>
                <p style="color:#bdc3c7; font-size:13px;">趨向：{chan_name}</p>
            </div>
            """, unsafe_allow_html=True)

        with col_r:
            st.markdown('<div class="glass-card"><h3 style="color:#2d3436; margin-top:0;">📜 大師天解</h3><hr style="border:0.5px solid #f9f9f9;">', unsafe_allow_html=True)
            
            # --- 關鍵修復：放寬安全設定 ---
            safety_settings = [
                {"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            available_models = ['gemini-2.0-flash', 'gemini-3-flash-preview']
            success = False
            
            for m_name in available_models:
                try:
                    model = genai.GenerativeModel(m_name, safety_settings=safety_settings)
                    prompt = f"你是易經占卜大師。問題：{question}。卦象：{gua_name}變{chan_name}。請簡短精闢地以繁體中文解析局勢與建議。"
                    
                    response = model.generate_content(prompt, stream=True, request_options={"timeout": 60})
                    
                    placeholder = st.empty()
                    full_text = ""
                    
                    # 逐字讀取並檢查內容
                    for chunk in response:
                        try:
                            if chunk.text:
                                full_text += chunk.text
                                placeholder.markdown(f'<div style="color:#2d3436; line-height:1.8; font-size:17px;">{full_text}▌</div>', unsafe_allow_html=True)
                        except (ValueError, exceptions.InternalServerError):
                            # 如果 chunk 沒內容或被過濾
                            continue
                    
                    if full_text:
                        placeholder.markdown(f'<div style="color:#2d3436; line-height:1.8; font-size:17px;">{full_text}</div>', unsafe_allow_html=True)
                        success = True
                        break 
                except Exception:
                    continue 
            
            if not success:
                st.info("🏮 天機隱晦：AI 暫時無法解讀此問題（或內容被系統過濾），請換個問法試試看。")
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
