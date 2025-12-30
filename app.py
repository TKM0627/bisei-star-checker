import streamlit as st
import requests
import pandas as pd
import datetime

# --- 設定とデータ取得 ---
LAT, LON = 34.665, 133.46 # 井原市
URL = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=cloud_cover_mean&past_days=5&timezone=Asia%2FTokyo"

@st.cache_data
def get_weather_df():
    data = requests.get(URL).json()["daily"]
    return pd.DataFrame({
    "date": pd.Series(pd.to_datetime(data["time"])).dt.date, 
    "cloud": data["cloud_cover_mean"]
})

def get_moon_age(d):
    # 簡易月齢計算（誤差あり）
    diff = (d - datetime.date(2024, 1, 11)).days # 2024/1/11を新月とする
    return diff % 29.53

# --- UI ---
st.title("🌌 美星・星空予測ダッシュボード")
df = get_weather_df()

# 日付選択（過去5日〜未来7日）
selected_date = st.date_input("観測予定日を選択", value=datetime.date.today(), min_value=df["date"].min(), max_value=df["date"].max())

# スコア計算
cloud = df.loc[df["date"] == selected_date, "cloud"].values[0]
moon_age = get_moon_age(selected_date)
score = int(max(0, 70 - cloud * 0.7) + (abs(15 - moon_age) / 15) * 30)

# 表示
st.metric(f"{selected_date} の星空スコア", f"{score} / 100 点")
st.write(f"☁️ 平均雲量: {cloud}% | 🌙 推定月齢: {moon_age:.1f}")

if score > 80: st.success("絶好の観測チャンスです！")
elif score > 50: st.info("観測できそうです。防寒対策を忘れずに。")
else: st.warning("条件が良くありません。別の日を検討しましょう。")

st.subheader("前後1週間の雲量トレンド")
st.line_chart(df.set_index("date"))


