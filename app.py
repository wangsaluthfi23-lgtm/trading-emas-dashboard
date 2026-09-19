"""
Dashboard Backtest Emas (GC=F) — Tim Kehidupan / proyek Trading
Sumber data: data/hasil-backtest-d1.csv (5 th) dan
data/hasil-backtest-dua-metode-10y.csv (10 th, versi awal/kasar).

Jalankan lokal:  streamlit run dashboard/app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent / "data"

KOLOM_PCT = ["win_rate", "profit_factor"]
KOLOM_NUM = ["trades", "net_r", "max_dd_r", "growth_1pct", "avg_r"]


@st.cache_data
def load_hasil_5y() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "hasil-backtest-d1.csv")
    df["kombinasi"] = (
        df["metode"]
        + " · SL="
        + df["sl_atr"].astype(str)
        + " TP="
        + df["tp_atr"].astype(str)
        + " · "
        + df["filter"].fillna("-")
    )
    return df


@st.cache_data
def load_hasil_10y() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "hasil-backtest-dua-metode-10y.csv")
    df["kombinasi"] = (
        df["metode"]
        + " · SL="
        + df["sl_atr"].astype(str)
        + " TP="
        + df["tp_atr"].astype(str)
    )
    # Laporkan duplikat (ditemukan saat audit 19 Sep 2026): baris kembar di file.
    df["duplikat"] = df.duplicated(subset=["metode", "sl_atr", "tp_atr"], keep=False)
    return df


def buat_label(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["pf"] = df["profit_factor"]
    df["win%"] = df["win_rate"] * 100
    df["growth%"] = df["growth_1pct"] * 100
    return df


st.set_page_config(page_title="Backtest Emas GC=F", page_icon="📈", layout="wide")

st.title("📈 Dashboard Backtest Emas (GC=F)")
st.caption("Sumber: `proyek/Trading/data` — update 19 Sep 2026.")

df5 = load_hasil_5y().pipe(buat_label)
df10 = load_hasil_10y()

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Filter")
    metode = st.multiselect(
        "Metode", sorted(df5["metode"].unique()), default=sorted(df5["metode"].unique())
    )
    f_ema = st.radio("Filter EMA50", ["Semua", "Tanpa filter", "Dengan EMA50"], index=0)
    sort_by = st.selectbox(
        "Urutkan berdasar",
        ["growth%", "pf", "net_r", "win%", "trades"],
        format_func=lambda c: {
            "growth%": "Pertumbuhan 1% (terbaik →)",
            "pf": "Profit factor",
            "net_r": "Net R",
            "win%": "Win rate",
            "trades": "Jumlah trade",
        }[c],
    )

tab5, tab10 = st.tabs(["Hasil 5 Tahun (final)", "Hasil 10 Tahun (kasar)"])

with tab5:
    df = df5[df5["metode"].isin(metode)].copy()
    if f_ema == "Tanpa filter":
        df = df[df["filter"].isna() | (df["filter"] == "-")]
    elif f_ema == "Dengan EMA50":
        df = df[df["filter"] == "EMA50"]

    if df.empty:
        st.warning("Tidak ada kombinasi yang cocok dengan filter. Ubah pilihan di sidebar.")
    else:
        profitable = df[df["pf"] > 1.2]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Kombinasi lolos filter", f"{len(df)}")
        c2.metric("Profit factor terbaik", f"{df['pf'].max():.2f}",
                  df.loc[df['pf'].idxmax(), 'kombinasi'])
        c3.metric("Pertumbuhan tertinggi", f"{df['growth%'].max():.1f}%",
                  df.loc[df['growth%'].idxmax(), 'kombinasi'])
        c4.metric("Kombinasi PF > 1.2", f"{len(profitable)}")

        st.subheader("Top 10 pertumbuhan")
        top = df.nlargest(10, "growth%")
        fig = px.bar(
            top,
            x="kombinasi",
            y="growth%",
            color="pf",
            color_continuous_scale=["#ef4444", "#f59e0b", "#22c55e"],
            labels={"kombinasi": "", "growth%": "Pertumbuhan (%)", "pf": "PF"},
        )
        fig.update_layout(xaxis_tickangle=-45, height=420, margin=dict(t=10, b=10))
        st.plotly_chart(fig, width="stretch")

        st.subheader("Win rate vs Profit factor")
        scat = px.scatter(
            df,
            x="win%",
            y="pf",
            size="trades",
            color="metode",
            hover_name="kombinasi",
            labels={"win%": "Win rate (%)", "pf": "Profit factor"},
        )
        scat.add_hline(y=1.2, line_dash="dot", line_color="#22c55e",
                       annotation_text="PF 1.2")
        scat.update_layout(height=420)
        st.plotly_chart(scat, width="stretch")

        st.subheader("Semua kombinasi")
        df = df.sort_values(sort_by, ascending=False)
        st.dataframe(
            df[
                [
                    "kombinasi", "trades", "win%", "pf", "net_r",
                    "max_dd_r", "growth%", "avg_r", "buy", "sell",
                ]
            ],
            width="stretch",
            height=420,
        )
        st.download_button(
            "⬇️ Unduh hasil (CSV)",
            df.to_csv(index=False).encode("utf-8"),
            file_name="hasil-backtest-filter.csv",
            mime="text/csv",
        )

with tab10:
    st.info(
        "Versi ini masih KASAR — tiap kombinasi cuma 4 trade (n_trade=4) dan ada "
        "baris duplikat di sumbernya. Belum layak dipakai buat keputusan; "
        "bakal diulang beneran setelah MT5 login & data intraday siap."
    )
    n_dup = int(df10["duplikat"].sum())
    c1, c2 = st.columns(2)
    c1.metric("Baris duplikat di sumber", n_dup)
    c2.metric("Metode", df10["metode"].nunique())
    st.dataframe(df10.drop(columns=["duplikat"]), width="stretch")