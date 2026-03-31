import streamlit as st
import google.generativeai as genai

st.title("🧪 API 連線測試儀")

# 優先讀取 Secrets，若無則顯示輸入框
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("輸入 API Key 測試", type="password")

if st.button("測試連線"):
    if not api_key:
        st.error("未偵測到 API Key")
    else:
        try:
            genai.configure(api_key=api_key)
            # 獲取目前帳號可用的模型清單
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            st.success(f"✅ 連線成功！您的 Key 支援以下模型：")
            st.write(models)
            
            # 嘗試實際生成一句話
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("你好，請說『天機已連線』")
            st.info(f"AI 回應：{response.text}")
            
        except Exception as e:
            st.error(f"❌ 連線失敗：{str(e)}")
            st.write("提示：請檢查 Streamlit Cloud 的 Secrets 設定名稱是否為 GEMINI_API_KEY")
