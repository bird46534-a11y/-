import streamlit as st
import random
import google.generativeai as genai
from google.api_core import exceptions

# --- 1. 頁面配置 ---
st.set_page_config(page_title="天機啟示錄 | 明亮版", layout="wide")

# --- 2. CSS 視覺：清新白底風格 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700&display=swap');
    
    /* 整體背景與字體 */
    .stApp {
        background-color: #f8f9fa;
        color: #2d3436;
        font-family: 'Noto Serif TC', serif;
    }
    
    /* 標題與副標題 */
    .main-title {
        text-align: center;
        color: #2d3436;
        letter-spacing: 12px;
        margin-bottom: 5px;
        font-weight: 700;
    }
    
    /* 卡片容器：白色浮雕感 */
    .glass-card {
        background: #ffffff;
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* 卦象線條：深灰與朱紅 */
    .gua-line {
        font-family: monospace;
        font-size: 48px;
        line-height: 1.1;
        text-align: center;
        margin: 5px 0;
    }
    
    /* 自定義按鈕樣式 */
    .stButton>button {
        background-color: #2d3436;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #636e72;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 核心邏輯 ---
def cast_iching():
    scores = [sum([random.choice([2, 3]) for _ in range(3)]) for _ in range(6)]
    bagua = {"111":"乾","000":"坤","100":"震","011":"巽","010":"坎","101":"離","001":"艮","110":"兌"}
    bin_str = "".join(["1" if s in [7, 9] else "0" for s in scores])
    up, down = bagua[bin_str[3:]], bagua[bin_str[:3]]
    # 簡易卦名字典
    names = {"111111":"乾為天", "000000":"坤為地", "110100":"風山漸", "101101":"離為火"}
    full_name = names.get(bin_str, f"{up}{down}卦")
    return scores, full_name

# --- 4. 主程式 ---
def main():
    st.markdown('<h1 class="main-title">☯ 天機啟示錄</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#95a5a6; margin-bottom:40px;">v4.7 MODERN LIGHT EDITION</p>', unsafe_allow_html=True)

    # API Key 配置
    api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("輸入 API Key", type="password")

    # 輸入區
    with st.container():
        question = st.text_input("🔮 欲請教天機之事：", placeholder="請在此輸入您的疑惑...")
        btn = st.button("啟動占卜儀式", use_container_width=True)

    if btn:
        if not api_key:
            st.error("❌ 系統缺少 API 金鑰，請於側邊欄輸入或設定 Secrets。")
            return

        scores, gua_name = cast_iching()
        
        # 配置 AI
        genai.configure(api_key=api_key)
        # 使用您清單中穩定的 2.0 版本
        model_name = 'gemini-2.0-flash' 
        model = genai.GenerativeModel(model_name)

        col_l, col_r = st.columns([1, 1.5], gap="large")
        
        with col_l:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;">
                <h2 style="color:#2d3436; border-bottom: 2px solid #f1c40f; display:inline-block; padding-bottom:5px;">{gua_name}</h2>
                <div style="margin:30px 0;">
                {"".join([f"<div class='gua-line' style='color:{('#d63031' if s in [7,9] else '#2d3436')};'>{'━━━━━━' if s in [7,9] else '━━━&nbsp;&nbsp;&nbsp;━━━'}{' <span style=\"color:#f1c40f; font-size:24px;\">●</span>' if s in [6,9] else ''}</div>" for s in reversed(scores)])}
                </div>
                <p style="color:#636e72; font-size:14px;">紅線為陽，黑線為陰；圓點為動爻</p>
            </div>
            """, unsafe_allow_html=True)

        with col_r:
            st.markdown('<div class="glass-card"><h3 style="color:#2d3436;">📜 大師指點</h3><hr style="border:0.5px solid #eee;">', unsafe_allow_html=True)
            try:
                # 使用流式傳輸解決超時與等待感
                prompt = f"你是易經大師。問題：{question}。卦象：{gua_name}。請簡短精闢地解析局勢與行動建議。請使用繁體中文並適度排版。"
                response = model.generate_content(prompt, stream=True, request_options={"timeout": 60})
                
                placeholder = st.empty()
                full_text = ""
                for chunk in response:
                    full_text += chunk.text
                    placeholder.markdown(f'<div style="color:#2d3436; line-height:1.8;">{full_text}▌</div>', unsafe_allow_html=True)
                placeholder.markdown(f'<div style="color:#2d3436; line-height:1.8;">{full_text}</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"🔮 天機感應中斷：{str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
