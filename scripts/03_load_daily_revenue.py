import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import numpy as np

# ============================================================
# FLAMES PIZZA — Load daily_revenue data into PostgreSQL
# Source: Rajani Revenue sheet (Raw Data) (2).xlsx
# ============================================================

# --- File path ---
FILE_PATH = '/Users/Ashwin/Downloads/Rajani Revenue sheet (Raw Data) (2).xlsx'

# --- Platform name standardisation ---
PLATFORM_MAP = {
    'swiggy'                        : 'swiggy',
    'smoked swiggy'                 : 'swiggy',
    'flames pizza - zomato'         : 'zomato',
    'smoked flames pizza - zomato'  : 'zomato',
    'dine in'                       : 'dine_in',
    'pick up'                       : 'pickup',
    'flames pizza - dotpe'          : 'dotpe',
    'uber eats'                     : 'ubereats',
    'flames pizza - magicpin'       : 'magicpin',
    'flames pizza  - eksecond'      : 'eksecond',
    'flames pizza - eksecond'       : 'eksecond',
    'flames pizza - ownly'          : 'ownly',
    'corporate'                     : 'corporate',
    'delivery'                      : 'delivery',
}

print("📂 Reading Excel file...")
df = pd.read_excel(FILE_PATH)

print(f"✅ Loaded {len(df)} rows")
print(f"   Columns: {list(df.columns)}")

# --- Clean column names ---
df.columns = df.columns.str.strip()

# --- Rename columns to match database ---
df = df.rename(columns={
    'Date '                  : 'order_date',
    'Date'                   : 'order_date',
    'Time '                  : 'order_time',
    'Time'                   : 'order_time',
    'Day '                   : 'day_of_week',
    'Day'                    : 'day_of_week',
    'Revenue Stream'         : 'platform_raw',
    'My Amount (₹)'          : 'my_amount',
    'Total Discount (₹)'     : 'total_discount',
    'Packaging Charge (₹)'   : 'packaging_charge',
    'Net Amount (₹)'         : 'net_amount',
    'GST (₹)'                : 'gst',
    'Gross Amount(₹)'        : 'gross_amount',
    'Hour '                  : 'hour_of_day',
    'Hour'                   : 'hour_of_day',
    'Month '                 : 'order_month',
    'Month'                  : 'order_month',
})

print("\n🧹 Cleaning data...")

# --- Parse dates ---
df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')

# --- Extract year ---
df['order_year'] = df['order_date'].dt.year

# --- Extract day of week from date (more reliable than the Day column) ---
df['day_of_week'] = df['order_date'].dt.strftime('%A')

# --- Format order_month as string ---
df['order_month'] = df['order_date'].dt.strftime('%B %Y')

# --- Clean order_time ---
df['order_time'] = df['order_time'].astype(str)
df['order_time'] = df['order_time'].replace('nan', None)
df['order_time'] = df['order_time'].replace('NaT', None)

# --- Standardise platform names ---
df['platform'] = df['platform_raw'].str.strip().str.lower().map(PLATFORM_MAP)
df['platform'] = df['platform'].fillna(df['platform_raw'].str.strip().str.lower())

# --- Clean numeric columns ---
numeric_cols = ['my_amount', 'total_discount', 'packaging_charge', 
                'net_amount', 'gst', 'gross_amount', 'hour_of_day']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# --- Add covid_period flag ---
df['covid_period'] = (
    (df['order_date'] >= '2020-04-01') & 
    (df['order_date'] <= '2022-03-31')
)

# --- Add data_type flag ---
df['data_type'] = df['order_time'].apply(
    lambda x: 'order_level' if x and x != 'None' and x != 'nan' else 'summary'
)

# --- Drop rows with no date ---
df = df.dropna(subset=['order_date'])

print(f"✅ Cleaned {len(df)} rows")
print(f"\n📊 Platform breakdown:")
print(df['platform'].value_counts())
print(f"\n📅 Date range: {df['order_date'].min().date()} to {df['order_date'].max().date()}")
print(f"🦠 COVID period rows: {df['covid_period'].sum()}")
print(f"📋 Summary rows: {(df['data_type'] == 'summary').sum()}")
print(f"🧾 Order level rows: {(df['data_type'] == 'order_level').sum()}")

# --- Connect to PostgreSQL ---
print("\n🔌 Connecting to PostgreSQL...")
conn = psycopg2.connect(
    dbname='flames_pizza',
    user='Ashwin',
    host='localhost',
    port='5432'
)
cur = conn.cursor()

# --- Prepare rows for insertion ---
print("📤 Loading data into daily_revenue table...")

rows = []
for _, row in df.iterrows():
    rows.append((
        row['order_date'].date() if pd.notna(row['order_date']) else None,
        row['order_time'] if row['order_time'] not in ['None', 'nan', 'NaT', ''] else None,
        row['day_of_week'],
        int(row['hour_of_day']) if row['hour_of_day'] and row['hour_of_day'] != 0 else None,
        row['order_month'],
        int(row['order_year']) if pd.notna(row['order_year']) else None,
        row['platform'],
        row['platform_raw'],
        float(row['my_amount']),
        float(row['total_discount']),
        float(row['packaging_charge']),
        float(row['net_amount']),
        float(row['gst']),
        float(row['gross_amount']),
        bool(row['covid_period']),
        row['data_type'],
    ))

# --- Insert in batches ---
insert_sql = """
    INSERT INTO daily_revenue (
        order_date, order_time, day_of_week, hour_of_day,
        order_month, order_year, platform, platform_raw,
        my_amount, total_discount, packaging_charge,
        net_amount, gst, gross_amount,
        covid_period, data_type
    ) VALUES %s
"""

execute_values(cur, insert_sql, rows, page_size=1000)
conn.commit()

print(f"✅ Successfully loaded {len(rows)} rows into daily_revenue!")

# --- Verify ---
cur.execute("SELECT COUNT(*) FROM daily_revenue")
count = cur.fetchone()[0]
print(f"✅ Verified: {count} rows now in daily_revenue table")

cur.execute("""
    SELECT order_year, COUNT(*) as rows, ROUND(SUM(gross_amount)::numeric, 2) as total_revenue
    FROM daily_revenue
    GROUP BY order_year
    ORDER BY order_year
""")
print("\n📊 Revenue by year:")
print(f"{'Year':<8} {'Rows':<10} {'Total Revenue'}")
print("-" * 35)
for row in cur.fetchall():
    print(f"{row[0]:<8} {row[1]:<10} ₹{row[2]:,.2f}")

cur.close()
conn.close()
print("\n🎉 Done! Your data is now in PostgreSQL.")
