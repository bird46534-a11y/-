import streamlit as st
import random
import google.generativeai as genai
from google.api_core import exceptions

# --- 1. 頁面配置 ---
st.set_page_config(page_title="天機啟示錄 2026", layout="wide")

# --- 2. CSS (精簡視覺) ---
st.markdown("""
<style>
    .stApp { background: #0e1117; color: #e0e0e0; font-family: sans-serif; }
    .glass-card { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 20px; border: 1px solid #333; }
    .gua-line { font-family: monospace; font-size: 40px; line-height: 1.1; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 3. 占卜引擎 ---
def cast_gua():
    scores = [sum([random.choice([2, 3]) for _ in range(3)]) for _ in range(6)]
    bagua = {"111":"乾","000":"坤","100":"震","011":"巽","010":"坎","101":"離","001":"艮","110":"兌"}
    def get_info(s_list):
        bin_str = "".join(["1" if s in [7, 9] else "0" for s in s_list])
        up, down = bagua[bin_str[3:]], bagua[bin_str[:3]]
        return f"{up}{down}卦"
    return scores, get_info(scores)

# --- 4. 主程式 ---
def main():
    st.title("☯️ 天機啟示錄 v4.5")
    
    api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("API Key", type="password")

    question = st.text_input("🔮 欲請教之事：", placeholder="輸入後點擊下方按鈕...")

    if st.button("啟動占卜", use_container_width=True):
        if not api_key:
            st.error("請提供 API Key")
            return

        scores, gua_name = cast_gua()
        
        # 配置 AI
        genai.configure(api_key=api_key)
        
        # 嘗試使用更輕量、更快的模型
        model_name = 'gemini-3-flash-preview' 
        model = genai.GenerativeModel(model_name)

        with st.spinner("⚡ 天機讀取中，請稍候..."):
            try:
                # 加入 timeout 限制 (30秒)，避免無限等待
                response = model.generate_content(
                    f"你是易經大師。問題：{question}。卦象：{gua_name}。請用三句話簡短解析，HTML 格式。",
                    request_options={"timeout": 30}
                )
                ai_msg = response.text
                
                # 顯示結果
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"<div class='glass-card'><h2>{gua_name}</h2>" + 
                                "".join([f"<div class='gua-line' style='color:{('#ff4d4d' if s in [7,9] else '#00d2ff')}'>{'━━━' if s in [7,9] else '━ ━'}</div>" for s in reversed(scores)]) + 
                                "</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div class='glass-card'><h3>📜 天啟</h3>{ai_msg}</div>", unsafe_allow_html=True)
                    
            except exceptions.DeadlineExceeded:
                st.error("⏳ 天機超時：伺服器反應過慢，請再試一次。")
            except Exception as e:
                st.error(f"❌ 連線失敗：{str(e)}")
                st.info("提示：這可能是模型代號暫時不穩定，請重整網頁。")

if __name__ == "__main__":
    main()
