import streamlit as st
import random
import datetime
import google.generativeai as genai

# --- 1. 頁面配置 (寬螢幕模式) ---
st.set_page_config(
    page_title="天機啟示錄 | 數位祭壇 2026",
    page_icon="☯️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. 極致視覺 CSS (黑金琉璃) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700&display=swap');
    
    /* 核心背景與字體 */
    .stApp {
        background: radial-gradient(circle at top right, #1a1a1a, #000000);
        color: #e0e0e0;
        font-family: 'Noto Serif TC', serif;
    }
    
    /* 卦象線條樣式 */
    .gua-line {
        font-family: monospace;
        font-size: 50px;
        line-height: 1.1;
        text-shadow: 0 0 20px rgba(255,255,255,0.1);
        user-select: none;
    }
    
    /* 動爻閃爍動畫 */
    @keyframes blink { 0%, 100% { opacity: 1; filter: drop-shadow(0 0 5px #f1c40f); } 50% { opacity: 0.3; } }
    .moving-yao { 
        animation: blink 1.5s infinite; 
        color: #f1c40f !important; 
        margin-left: 15px;
        font-size: 20px;
    }

    /* 玻璃質感容器 */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 35px;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        box-shadow: 0 25px 50px rgba(0,0,0,0.5);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 核心占卜引擎 ---
class IChingEngine:
    def __init__(self):
        self.bagua = {"111":"乾","000":"坤","100":"震","011":"巽","010":"坎","101":"離","001":"艮","110":"兌"}
        self.hex_names = {
            "111111":"乾為天", "000000":"坤為地", "110100":"風山漸", 
            "111001":"山天大畜", "101101":"離為火", "010010":"坎為水"
        }

    def cast(self):
        return [sum([random.choice([2, 3]) for _ in range(3)]) for _ in range(6)]

    def get_info(self, bin_str):
        up, down = self.bagua[bin_str[3:]], self.bagua[bin_str[:3]]
        name = self.hex_names.get(bin_str, f"{up}{down}卦")
        elements = {"乾":"金","坤":"土","震":"木","巽":"木","坎":"水","離":"火","艮":"土","兌":"金"}
        return {"name": name, "element": elements.get(down, "未知")}

# --- 4. 主程式介面 ---
def main():
    # 標題區
    st.markdown('<div style="text-align:center; margin-bottom:40px;"><h1 style="color:#f1c40f; letter-spacing:12px; font-size:45px;">☯ 天機啟示錄</h1><p style="color:#555; letter-spacing:5px;">DIGITAL DIVINATION v4.2 PRO</p></div>', unsafe_allow_html=True)

    # API Key 邏輯：優先 Secrets
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        with st.sidebar:
            st.warning("⚠️ 未在 Secrets 偵測到金鑰")
            api_key = st.text_input("手動輸入 Gemini API Key", type="password")

    # 輸入問題
    question = st.text_input("🔮 欲請教天機之事：", placeholder="請輸入您的疑惑...")

    if st.button("啟動占卜儀式", use_container_width=True):
        if not api_key:
            st.error("❌ 系統缺少 API 金鑰，無法連結天機。")
            return
        
        # 1. 執行占卜
        engine = IChingEngine()
        scores = engine.cast()
        orig_bin = "".join(["1" if s in [7, 9] else "0" for s in scores])
        chan_bin = "".join([("0" if s == 9 else "1" if s == 6 else "1" if s == 7 else "0") for s in scores])
        
        orig = engine.get_info(orig_bin)
        chan = engine.get_info(chan_bin)
        
        # 2. 配置 AI (修正 404 問題)
        try:
            genai.configure(api_key=api_key)
            # 2026 推薦使用更穩定的模型代碼
            model = genai.GenerativeModel('gemini-1.5-flash') 
            
            with st.spinner("正在撥開雲霧，解讀卦象能量..."):
                prompt = f"""
                你是一位精通易經與時空規律的占卜宗師。
                問題：『{question}』
                本卦：{orig['name']} (五行：{orig['element']})
                變卦：{chan['name']}
                爻數得分(初至上)：{scores} (6老陰/9老陽為動爻)
                請根據五行生剋與卦辭提供深度解析，使用繁體中文，HTML 格式輸出。
                包含：[局勢分析]、[動爻戒語]、[一語天機]。
                """
                response = model.generate_content(prompt)
                ai_msg = response.text

            # 3. 畫面呈現 (左右寬螢幕佈局)
            col_left, col_right = st.columns([1, 2], gap="large")
            
            with col_left:
                # 繪製卦象
                lines_html = ""
                for s in reversed(scores):
                    color = "#ff4d4d" if s in [7, 9] else "#00d2ff"
                    line_shape = "━━━━━━" if s in [7, 9] else "━━━&nbsp;&nbsp;&nbsp;━━━"
                    moving = '<span class="moving-yao">★</span>' if s in [6, 9] else ""
                    lines_html += f"<div class='gua-line' style='color:{color};'>{line_shape}{moving}</div>"

                st.markdown(f"""
                <div class="glass-card" style="text-align:center;">
                    <div style="color:#f1c40f; font-size:14px; letter-spacing:3px; margin-bottom:10px;">PRESENT HEXAGRAM</div>
                    <h2 style="font-size:42px; margin-bottom:25px;">{orig['name']}</h2>
                    {lines_html}
                    <div style="margin-top:30px; border-top:1px solid #333; padding-top:20px; display:flex; justify-content:space-around; font-size:14px;">
                        <span>五行：{orig['element']}</span>
                        <span>趨向：{chan['name']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_right:
                st.markdown(f"""
                <div class="glass-card" style="min-height:450px;">
                    <div style="color:#f1c40f; font-weight:bold; margin-bottom:20px; font-size:20px;">📜 大師天解</div>
                    <div style="line-height:1.9; color:#ced6e0; font-size:17px;">{ai_msg}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.caption(f"觀測時間：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        except Exception as e:
            st.error(f"🔮 天機連線異常：{str(e)}")
            st.info("建議：請檢查 Secrets 中的 API Key 是否正確，或嘗試更換模型代號。")

if __name__ == "__main__":
    main()
