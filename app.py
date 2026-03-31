import streamlit as st
import random
import datetime
import google.generativeai as genai

# --- 1. 頁面配置 ---
st.set_page_config(
    page_title="天機啟示錄 | 數位祭壇 2026",
    page_icon="☯️",
    layout="wide"
)

# --- 2. CSS 視覺優化 (黑金琉璃) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700&display=swap');
    .stApp { background: radial-gradient(circle at top right, #1a1a1a, #000000); color: #e0e0e0; font-family: 'Noto Serif TC', serif; }
    .gua-line { font-family: monospace; font-size: 50px; line-height: 1.1; text-shadow: 0 0 20px rgba(255,255,255,0.1); }
    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
    .moving-yao { animation: blink 1.5s infinite; color: #f1c40f !important; margin-left: 15px; font-size: 20px; }
    .glass-card { background: rgba(255, 255, 255, 0.03); padding: 35px; border-radius: 30px; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); box-shadow: 0 25px 50px rgba(0,0,0,0.5); }
</style>
""", unsafe_allow_html=True)

# --- 3. 核心引擎 ---
class IChingEngine:
    def __init__(self):
        self.bagua = {"111":"乾","000":"坤","100":"震","011":"巽","010":"坎","101":"離","001":"艮","110":"兌"}
    def cast(self): return [sum([random.choice([2, 3]) for _ in range(3)]) for _ in range(6)]
    def get_info(self, bin_str):
        up, down = self.bagua[bin_str[3:]], self.bagua[bin_str[:3]]
        db = {"111111":"乾為天", "000000":"坤為地", "110100":"風山漸", "111001":"山天大畜", "101101":"離為火"}
        name = db.get(bin_str, f"{up}{down}卦")
        elements = {"乾":"金","坤":"土","震":"木","巽":"木","坎":"水","離":"火","艮":"土","兌":"金"}
        return {"name": name, "element": elements.get(down, "未知")}

# --- 4. 主程式 ---
def main():
    st.markdown('<div style="text-align:center; margin-bottom:40px;"><h1 style="color:#f1c40f; letter-spacing:10px;">☯ 天機啟示錄</h1><p style="color:#444;">DIGITAL ALTAR v4.4 - GEMINI 3 FLASH READY</p></div>', unsafe_allow_html=True)

    # API Key 獲取
    api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("手動輸入 API Key", type="password")

    question = st.text_input("🔮 欲請教天機之事：", placeholder="輸入您的疑惑...")

    if st.button("啟動占卜儀式", use_container_width=True):
        if not api_key:
            st.error("❌ 系統缺少 API 金鑰。")
            return
        
        engine = IChingEngine()
        scores = engine.cast()
        orig_bin = "".join(["1" if s in [7, 9] else "0" for s in scores])
        orig = engine.get_info(orig_bin)
        chan_name = engine.get_info("".join([("0" if s == 9 else "1" if s == 6 else "1" if s == 7 else "0") for s in scores]))['name']

        # 配置 AI - 使用您清單中支援的模型
        try:
            genai.configure(api_key=api_key)
            
            # 根據您的偵測結果，鎖定 Gemini 3 系列
            model_code = 'gemini-3-flash-preview' 
            model = genai.GenerativeModel(model_code)
            
            with st.spinner(f"正在連線至天機伺服器 ({model_code})..."):
                prompt = f"""
                你是一位精通易經占卜與未來學的 AI 大師。
                當前時間為 2026 年仲春。
                問題：『{question}』
                占卜結果：本卦【{orig['name']}】，變卦【{chan_name}】。
                請根據五行生剋與卦義，為使用者提供精闢的解析。
                輸出格式：HTML 片段，包含 [局勢分析]、[行動指引]、[一語破天機]。
                """
                response = model.generate_content(prompt)
                ai_msg = response.text

            # 畫面渲染
            col_l, col_r = st.columns([1, 2], gap="large")
            with col_l:
                lines = ""
                for s in reversed(scores):
                    c = "#ff4d4d" if s in [7, 9] else "#00d2ff"
                    shape = "━━━━━━" if s in [7, 9] else "━━━&nbsp;&nbsp;&nbsp;━━━"
                    m = '<span class="moving-yao">★</span>' if s in [6, 9] else ""
                    lines += f"<div class='gua-line' style='color:{c};'>{shape}{m}</div>"
                st.markdown(f'<div class="glass-card" style="text-align:center;"><h2>{orig["name"]}</h2>{lines}<br>五行：{orig["element"]}</div>', unsafe_allow_html=True)
            
            with col_r:
                st.markdown(f'<div class="glass-card" style="min-height:400px;">{ai_msg}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"🔮 天機異常：{str(e)}")
            st.info("提示：若仍出現 404，請嘗試將代碼中的 'gemini-3-flash-preview' 改為 'gemini-pro-latest'。")

if __name__ == "__main__":
    main()
