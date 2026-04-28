# 💪 AI Protein Tracker: Smart Macro Logging

Aplikasi berbasis Python dan Streamlit yang dirancang untuk membantu antusias fitness mencatat asupan protein harian secara cepat menggunakan **Natural Language Input**. Proyek ini menggunakan algoritma pencocokan teks cerdas dan penyimpanan data persisten.

## 🌟 Fitur Utama
- **NLP Text Input:** Input bebas seperti "2 telur utuh dan 100g dada ayam".
- **Fuzzy Matching Logic:** Mengenali nama makanan meskipun ada typo atau penulisan yang tidak standar.
- **Varian Telur Spesifik:** Mendukung pemisahan nutrisi antara telur utuh dan putih telur.
- **Persistent SQLite Database:** Riwayat makan tersimpan secara lokal dan tidak hilang saat aplikasi ditutup.
- **Real-time Dashboard:** Visualisasi total protein harian terhadap target.

## 🛠️ Tech Stack
- **Framework:** Streamlit
- **Language:** Python 3.x
- **Matching Library:** FuzzyWuzzy (Levenshtein Distance)
- **Database:** SQLite3
- **Data Handling:** Pandas & Regex

## 📋 Requirements
Pastikan library berikut terinstal:
```bash
pip install pandas streamlit fuzzywuzzy python-Levenshtein