import streamlit as st
import random
import google.generativeai as genai
from google.api_core import exceptions
import time

# --- 1. 頁面配置 ---
st.set_page_config(page_title="天機啟示錄 | 現代白底版", layout="wide")

# --- 2. CSS 視覺：清新白底風格 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700&display=swap');
    
    .stApp {
        background-color: #f8f9fa;
        color: #2d3436;
        font-family: 'Noto Serif TC', serif;
    }
    
    .main-title {
        text-align: center;
        color: #2d3436;
        letter-spacing: 10px;
        margin-bottom: 5px;
        font-weight: 700;
    }
    
    .glass-card {
        background: #ffffff;
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    .gua-line {
        font-family: monospace;
        font-size: 48px;
        line-height: 1.1;
        text-align: center;
        margin: 5px 0;
        user-select: none;
    }
    
    .stButton>button {
        background-color: #2d3436;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 12px 20px;
        font-size: 16px;
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #636e72;
        color: white;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 核心占卜邏輯 ---
def cast_iching():
    scores = [sum([random.choice([2, 3]) for _ in range(3)]) for _ in range(6)]
    bagua = {"111":"乾","000":"坤","100":"震","011":"巽","010":"坎","101":"離","001":"艮","110":"兌"}
    bin_str = "".join(["1" if s in [7, 9] else "0" for s in scores])
    up, down = bagua[bin_str[3:]], bagua[bin_str[:3]]
    # 擴充簡易卦名
    names = {"111111":"乾為天", "000000":"坤為地", "110100":"風山漸", "101101":"離為火", "010010":"坎為水"}
    full_name = names.get(bin_str, f"{up}{down}卦")
    return scores, full_name

# --- 4. 主程式 ---
def main():
    st.markdown('<h1 class="main-title">☯ 天機啟示錄</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#95a5a6; margin-bottom:30px;">v4.8 STABLE LIGHT EDITION</p>', unsafe_allow_html=True)

    # API Key 配置 (優先從 Secrets 讀取)
    api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("輸入 API Key", type="password")

    # 輸入區
    question = st.text_input("🔮 欲請教天機之事：", placeholder="請輸入您的疑惑，例如：今年事業運勢？")
    
    if st.button("啟動占卜儀式"):
        if not api_key:
            st.error("❌ 系統缺少 API 金鑰，請於 Secrets 設定 GEMINI_API_KEY。")
            return

        scores, gua_name = cast_iching()
        genai.configure(api_key=api_key)

        # 佈局設定
        col_l, col_r = st.columns([1, 1.5], gap="large")
        
        with col_l:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;">
                <h2 style="color:#2d3436; border-bottom: 2px solid #f1c40f; display:inline-block; padding-bottom:5px;">{gua_name}</h2>
                <div style="margin:30px 0;">
                {"".join([f"<div class='gua-line' style='color:{('#d63031' if s in [7,9] else '#2d3436')};'>{'━━━━━━' if s in [7,9] else '━━━&nbsp;&nbsp;&nbsp;━━━'}{' <span style=\"color:#f1c40f; font-size:24px;\">●</span>' if s in [6,9] else ''}</div>" for s in reversed(scores)])}
                </div>
                <p style="color:#b2bec3; font-size:13px;">朱紅為陽，墨黑為陰；金點為動爻</p>
            </div>
            """, unsafe_allow_html=True)

        with col_r:
            res_box = st.container()
            with res_box:
                st.markdown('<div class="glass-card"><h3 style="color:#2d3436; margin-top:0;">📜 大師指點</h3><hr style="border:0.5px solid #eee;">', unsafe_allow_html=True)
                
                # 模型嘗試清單 (自動降級機制)
                model_list = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-pro']
                success = False
                
                for m_name in model_list:
                    try:
                        model = genai.GenerativeModel(m_name)
                        prompt = f"你是易經大師。問題：{question}。卦象：{gua_name}。請簡短精闢地解析局勢與行動建議。請使用繁體中文。"
                        
                        # 流式傳輸
                        response = model.generate_content(prompt, stream=True, request_options={"timeout": 40})
                        
                        placeholder = st.empty()
                        full_text = ""
                        for chunk in response:
                            full_text += chunk.text
                            placeholder.markdown(f'<div style="color:#2d3436; line-height:1.8; font-size:17px;">{full_text}▌</div>', unsafe_allow_html=True)
                        placeholder.markdown(f'<div style="color:#2d3436; line-height:1.8; font-size:17px;">{full_text}</div>', unsafe_allow_html=True)
                        
                        success = True
                        break # 成功則跳出模型循環
                        
                    except exceptions.ResourceExhausted:
                        continue # 嘗試下一個模型
                    except Exception as e:
                        if "429" in str(e):
                            continue
                        st.error(f"感應異常 ({m_name})：{str(e)}")
                        break
                
                if not success:
                    st.warning("🏮 天機繁忙：目前所有模型配額已滿。請等待約 30 秒後再次嘗試，或稍後再回來。")
                
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
