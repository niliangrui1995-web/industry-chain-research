import pandas as pd

idx_path = r"d:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\verified_2016_present\market_data_audit\index_comparison_399006.csv"
margin_path = r"d:\vcp_hunter\产业链投研\artifacts\leverage_capitulation\verified_2016_present\official_margin_audit\verified_margin_balances.csv"

df_idx = pd.read_csv(idx_path)
df_margin = pd.read_csv(margin_path)

df_idx['date'] = df_idx['date'].astype(str)
df_margin['date'] = df_margin['date'].astype(str)

# Sort by date
df_idx = df_idx.sort_values('date').reset_index(drop=True)
df_margin = df_margin.sort_values('date').reset_index(drop=True)

# Helper function to get index info
def get_idx_info(d):
    row = df_idx[df_idx['date'] == d]
    if len(row) > 0:
        return {
            'close': row.iloc[0]['local_close'],
            'open': row.iloc[0]['local_open'],
            'high': row.iloc[0]['local_high'],
            'low': row.iloc[0]['local_low']
        }
    return None

# Helper function to get margin info
def get_margin_info(d):
    row = df_margin[df_margin['date'] == d]
    if len(row) > 0:
        return row.iloc[0]['total_margin_y']
    return None

# Period 1: 2021-02-18 to 2021-03-09
idx_start_1 = get_idx_info('2021-02-18')
idx_end_1 = get_idx_info('2021-03-09')
margin_start_1 = get_margin_info('2021-02-18')
margin_end_1 = get_margin_info('2021-03-09')

# Let's also check the pre-holiday date 2021-02-10
idx_pre_1 = get_idx_info('2021-02-10')
margin_pre_1 = get_margin_info('2021-02-10')

print("=== Period 1: 2021-02-18 to 2021-03-09 ===")
print(f"2021-02-10 (Pre-holiday) - Index Close: {idx_pre_1['close']:.2f}, Margin Balance: {margin_pre_1:.2f} 亿元")
print(f"2021-02-18 (Start) - Index Open: {idx_start_1['open']:.2f}, High: {idx_start_1['high']:.2f}, Close: {idx_start_1['close']:.2f}, Margin Balance: {margin_start_1:.2f} 亿元")
print(f"2021-03-09 (End) - Index Close: {idx_end_1['close']:.2f}, Low: {idx_end_1['low']:.2f}, Margin Balance: {margin_end_1:.2f} 亿元")

# Calculations for Period 1
idx_drop_close_1 = (idx_end_1['close'] - idx_start_1['close']) / idx_start_1['close'] * 100
idx_drop_high_1 = (idx_end_1['close'] - idx_start_1['high']) / idx_start_1['high'] * 100
idx_drop_pre_close_1 = (idx_end_1['close'] - idx_pre_1['close']) / idx_pre_1['close'] * 100

margin_diff_1 = margin_end_1 - margin_start_1
margin_pct_1 = (margin_diff_1 / margin_start_1) * 100
margin_diff_pre_1 = margin_end_1 - margin_pre_1
margin_pct_pre_1 = (margin_diff_pre_1 / margin_pre_1) * 100

print(f"Index drop (Close-to-Close): {idx_drop_close_1:.2f}%")
print(f"Index drop (High-to-Close): {idx_drop_high_1:.2f}%")
print(f"Index drop (PreClose-to-Close): {idx_drop_pre_close_1:.2f}%")
print(f"Margin Balance Change: {margin_diff_1:.2f} 亿元 ({margin_pct_1:.2f}%)")
print(f"Margin Balance Change (from Pre-holiday): {margin_diff_pre_1:.2f} 亿元 ({margin_pct_pre_1:.2f}%)")

# Period 2: 2026-07-01 to 2026-07-17
idx_start_2 = get_idx_info('2026-07-01')
idx_end_2 = get_idx_info('2026-07-17')
margin_start_2 = get_margin_info('2026-07-01')
margin_end_2 = get_margin_info('2026-07-16') # Note: July 17 is missing in margin file

idx_pre_2 = get_idx_info('2026-06-30')
margin_pre_2 = get_margin_info('2026-06-30')

print("\n=== Period 2: 2026-07-01 to 2026-07-17 ===")
print(f"2026-06-30 (Pre-period) - Index Close: {idx_pre_2['close']:.2f}, Margin Balance: {margin_pre_2:.2f} 亿元")
print(f"2026-07-01 (Start) - Index Open: {idx_start_2['open']:.2f}, High: {idx_start_2['high']:.2f}, Close: {idx_start_2['close']:.2f}, Margin Balance: {margin_start_2:.2f} 亿元")
print(f"2026-07-17 (End) - Index Close: {idx_end_2['close']:.2f}, Low: {idx_end_2['low']:.2f}")
print(f"2026-07-16 (Latest Margin) - Margin Balance: {margin_end_2:.2f} 亿元")

# Calculations for Period 2
idx_drop_close_2 = (idx_end_2['close'] - idx_start_2['close']) / idx_start_2['close'] * 100
idx_drop_high_2 = (idx_end_2['close'] - idx_start_2['high']) / idx_start_2['high'] * 100
idx_drop_pre_close_2 = (idx_end_2['close'] - idx_pre_2['close']) / idx_pre_2['close'] * 100

margin_diff_2 = margin_end_2 - margin_start_2
margin_pct_2 = (margin_diff_2 / margin_start_2) * 100
margin_diff_pre_2 = margin_end_2 - margin_pre_2
margin_pct_pre_2 = (margin_diff_pre_2 / margin_pre_2) * 100

print(f"Index drop (Close-to-Close): {idx_drop_close_2:.2f}%")
print(f"Index drop (High-to-Close): {idx_drop_high_2:.2f}%")
print(f"Index drop (PreClose-to-Close): {idx_drop_pre_close_2:.2f}%")
print(f"Margin Balance Change (from 07-01 to 07-16): {margin_diff_2:.2f} 亿元 ({margin_pct_2:.2f}%)")
print(f"Margin Balance Change (from 06-30 to 07-16): {margin_diff_pre_2:.2f} 亿元 ({margin_pct_pre_2:.2f}%)")
