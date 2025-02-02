import streamlit as st
import requests
from datetime import date

st.title("レース予測アプリ")

# 日付入力
race_date = st.date_input("レースの日付を選択", value=date.today())

# レース名入力
race_name = st.text_input("レース名を入力")

# 予測ボタン
if st.button("予測を実行"):
    if race_name:
        # APIリクエスト
        response = requests.post(
            "http://localhost:8000/predict",
            json={"date": str(race_date), "race_name": race_name}
        )
        
        if response.status_code == 200:
            result = response.json()
            st.write("予測結果:", result["prediction"])
        else:
            st.error("予測に失敗しました。")
    else:
        st.warning("レース名を入力してください。")
