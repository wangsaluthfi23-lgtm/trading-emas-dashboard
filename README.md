# Dashboard Backtest Emas (GC=F)

Dashboard interaktif hasil backtest 2 metode trading emas — **breakout** vs **momentum/zone** — dari proyek Trading Tim Kehidupan.

Data: `data/hasil-backtest-d1.csv` (5 tahun, final) + `data/hasil-backtest-dua-metode-10y.csv` (10 tahun, versi kasar).

## Jalankan lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy ke Streamlit Cloud

1. Push repo ini ke GitHub.
2. Buka [share.streamlit.io](https://share.streamlit.io) → **Create app**.
3. Pilih repo ini, branch `main`, file `app.py`.
4. Deploy — dashboard langsung kebuka dari HP.

## Isi dashboard

- **Tab 5 Tahun (final)**: filter metode (breakout/momentum), filter EMA50, top-10 pertumbuhan, scatter win rate vs profit factor, tabel semua kombinasi + tombol unduh CSV.
- **Tab 10 Tahun (kasar)**: peringatan data kasar + tabel kombinasi (belum layak buat keputusan).

> Disclaimer: hasil backtest bukan jaminan profit masa depan. Ini cuma alat belajar.