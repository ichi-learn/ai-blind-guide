import streamlit as st
import base64
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
import streamlit.components.v1 as components

st.set_page_config(page_title="AI Photo Analyzer", layout="centered")
st.title("📷 AI 写真解析")
st.write("ボタンを押して撮影すると、AIが内容を詳しく分析します。")

# 1. Azure AI Vision クライアントの初期化
# Secrets（.streamlit/secrets.toml）から読み込みます
client = ImageAnalysisClient(
    endpoint=st.secrets["AZURE_ENDPOINT"],
    credential=AzureKeyCredential(st.secrets["AZURE_KEY"])
)

# 2. カメラ入力（標準の camera_input を使用）
# これにより、ユーザーが自分のタイミングでシャッターを切れます
img_file = st.camera_input("カメラに向かって撮影してください", label_visibility="collapsed")

if img_file:
    # 撮影された画像をプレビュー表示（camera_inputが自動で行うため補足が必要な場合のみ）
    st.info("解析中... 少々お待ちください。")

    try:
        # 3. Azure AI Vision で解析実行
        # 画像のバイナリデータを取得して送信
        result = client.analyze(
            image_data=img_file.getvalue(),
            visual_features=[VisualFeatures.TAGS, VisualFeatures.CAPTION]
        )

        # 4. 結果の表示
        st.subheader("分析結果")

        # 文章で説明（Caption）
        if result.caption:
            st.write(f"**説明:** {result.caption.text}")
            
            # 音声合成（ブラウザに喋らせる）
            tts_script = f"""
            <script>
                var msg = new SpeechSynthesisUtterance('{result.caption.text}');
                msg.lang = 'en-US';
                window.speechSynthesis.speak(msg);
            </script>
            """
            components.html(tts_script, height=0)

        # タグで表示（Tags）
        tags = [tag.name for tag in result.tags.list if tag.confidence > 0.5]
        if tags:
            st.write(f"**キーワード:** {', '.join(tags)}")

    except Exception as e:
        st.error(f"解析中にエラーが発生しました: {e}")

# ヒント表示
st.sidebar.markdown("""
### 使い方
1. **Take Photo** ボタンを押して撮影。
2. そのまま解析結果が出るのを待つ。
3. 別のものを撮る時は **Clear photo** を押す。
""")