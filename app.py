import streamlit as st
import pandas as pd
import sqlite3
from fuzzywuzzy import process
import re
from datetime import datetime

# --- CONFIG & STYLES ---
st.set_page_config(page_title="Smart Protein Tracker", page_icon="💪", layout="centered")

# --- LOAD DATA & DATABASE ---
# Pastikan file nutrition_db.csv sudah ada atau gunakan data di bawah ini
@st.cache_data
def load_nutrition_db():
    data = {
        'food_item': [
            'dada ayam', 'paha ayam', 'telur utuh', 'putih telur', 'telur rebus', 
            'telur goreng', 'tempe', 'tahu', 'daging sapi', 'ikan salmon', 
            'ikan nila', 'ikan tongkol', 'whey protein', 'susu sapi', 'kacang tanah', 'nasi putih'
        ],
        'protein_per_unit': [
            0.31,  # dada ayam (per gram)
            0.26,  # paha ayam (per gram)
            6.5,   # telur utuh (per butir)
            3.6,   # putih telur (per butir)
            6.5,   # telur rebus (per butir)
            6.5,   # telur goreng (per butir)
            0.19,  # tempe (per gram)
            0.08,  # tahu (per gram)
            0.26,  # daging sapi (per gram)
            0.20,  # ikan salmon (per gram)
            0.26,  # ikan nila (per gram)
            0.24,  # ikan tongkol (per gram)
            24.0,  # whey protein (per scoop/gram - sesuaikan logika)
            0.034, # susu sapi (per ml)
            0.25,  # kacang tanah (per gram)
            0.027  # nasi putih (per gram)
        ],
        'unit_type': [
            'gram', 'gram', 'butir', 'butir', 'butir', 
            'butir', 'gram', 'gram', 'gram', 'gram', 
            'gram', 'gram', 'scoop', 'ml', 'gram', 'gram'
        ]
    }
    return pd.DataFrame(data)

df_nutrition = load_nutrition_db()

def save_to_db(food, protein):
    conn = sqlite3.connect('gym_tracker.db')
    c = conn.cursor()
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO logs (date, food, protein) VALUES (?, ?, ?)", (date_now, food, protein))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect('gym_tracker.db')
    # Pastikan tabel ada
    conn.execute("CREATE TABLE IF NOT EXISTS logs (date TEXT, food TEXT, protein REAL)")
    df = pd.read_sql_query("SELECT * FROM logs ORDER BY date DESC", conn)
    conn.close()
    return df

# --- LOGIKA PARSING CERDAS ---
def parse_and_calculate(user_input):
    items = re.findall(r'(\d+)\s*([a-zA-Z\s]+)', user_input.lower())
    results = []
    total_p = 0
    
    stop_words = ['gram', 'gr', 'dan', 'makan', 'saya', 'tadi', 'pagi', 'siang', 'malam', 'butir', 'potong']
    
    for qty, name in items:
        clean_name = name
        for word in stop_words:
            clean_name = clean_name.replace(word, '')
        clean_name = clean_name.strip()
        
        if not clean_name: continue
        
        match, score = process.extractOne(clean_name, df_nutrition['food_item'].tolist())
        
        if score > 50:
            row = df_nutrition[df_nutrition['food_item'] == match].iloc[0]
            qty = int(qty)
            
            if row['unit_type'] == 'butir' or row['unit_type'] == 'scoop':
                calc = qty * row['protein_per_unit']
                label = f"{qty} {row['unit_type']} {match}"
            else:
                weight = qty if ('gram' in name or 'gr' in name) else qty * 50
                calc = weight * row['protein_per_unit']
                label = f"{weight}g/ml {match}"
            
            # PINDAHKAN DUA BARIS INI KE LUAR BLOK ELSE (Sejajar dengan if row['unit_type'])
            total_p += calc
            results.append((label, round(calc, 1)))
            
    return results, total_p

# --- UI INTERFACE ---
st.title("💪 AI Protein Tracker")
st.markdown("Ketik makananmu (misal: *'2 telur dan 100g ayam'* atau *'1 ayam 2 tempe'*)")

user_input = st.text_input("Input Menu Makan", placeholder="Contoh: 1 telur 2 tempe")
btn_add = st.button("Hitung & Simpan")

if btn_add and user_input:
    parsed_items, total_protein = parse_and_calculate(user_input)
    
    if parsed_items:
        for item_name, p_val in parsed_items:
            save_to_db(item_name, p_val)
            st.success(f"✅ Dicatat: {item_name} ({p_val}g Protein)")
        st.balloons()
    else:
        st.error("Maaf, sistem tidak mengenali nama makanan atau jumlahnya.")

# --- DASHBOARD ---
st.divider()
history_df = get_history()

col1, col2 = st.columns(2)
with col1:
    total_today = history_df['protein'].sum() if not history_df.empty else 0
    st.metric("Total Protein Hari Ini", f"{total_today:.1f} g")

with col2:
    target = 120
    st.write(f"Target Harian: {target}g")
    st.progress(min(total_today / target, 1.0))

st.subheader("📜 Riwayat Makan")
st.dataframe(history_df, width='stretch')

if st.button("Reset Data"):
    conn = sqlite3.connect('gym_tracker.db')
    conn.execute("DROP TABLE IF EXISTS logs")
    conn.commit()
    conn.close()
    st.rerun()