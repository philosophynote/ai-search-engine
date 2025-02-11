import streamlit as st
import requests

# アプリのタイトル設定
st.title("AI検索エンジンインターフェース")

# サイドバーに設定情報
with st.sidebar:
    st.header("設定")
    api_url = st.text_input("APIエンドポイントURL", value="http://fastapi:8000/search")

# メインインターフェース
question = st.text_input("検索したい質問を入力してください", key="input_question")

if st.button("検索実行"):
    if not question:
        st.warning("質問を入力してください")
    else:
        try:
            # FastAPIへのリクエスト送信
            response = requests.post(
                api_url,
                json={"question": question},
                headers={"Content-Type": "application/json"},
            )

            # レスポンスの処理
            if response.status_code == 200:
                result = response.json()
                st.success("検索結果:")
                st.text(response)
                st.markdown(f"**回答**: {result['answer']}")
            else:
                st.error(f"エラーが発生しました: {response.text}")

        except requests.exceptions.ConnectionError:
            st.error(
                "APIサーバーに接続できませんでした。サーバーが起動しているか確認してください"
            )
        except Exception as e:
            st.error(f"予期せぬエラーが発生しました: {str(e)}")

# 実行方法の説明
st.markdown("""
### 実行方法
1. 別ターミナルでFastAPIサーバーを起動:
```bash
python -m uvicorn app.main:app --reload
```
2. 別ターミナルでStreamlitアプリを起動:
```bash
streamlit run streamlit_app.py
```
""")
