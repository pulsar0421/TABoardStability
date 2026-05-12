import datetime
import matplotlib.pyplot as plt
import pandas as pd
import os

filename = "20260512_Efficiency_shortterm_10s_m_.txt"

df = pd.read_csv(filename, sep=';')

df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Seoul')

for col in ['p_in', 'p_out', 'eff', 'temperature', 'temperature_room']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# KST filtering
start_time = datetime.time(15, 10, 10)
end_time = datetime.time(15, 11, 10)

filtered_df = df[
    (df['timestamp'].dt.time >= start_time) &
    (df['timestamp'].dt.time <= end_time)
].copy()

print(f'Full rows: {len(df)}, filtered rows: {len(filtered_df)}')
print(f'Available local time range: {df["timestamp"].min()} - {df["timestamp"].max()}')

if filtered_df.empty:
    raise ValueError("filtered_df is empty. Check start_time and end_time.")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

ax1.plot(filtered_df['timestamp'], filtered_df['p_in'], label='Input Power (mW)')
ax1.plot(filtered_df['timestamp'], filtered_df['p_out'], label='Output Power (mW)')
ax1.set_ylabel('Power (mW)')
ax1.set_title('Input and Output Power Over Time')
ax1.legend()
ax1.grid(True)

ax2.plot(filtered_df['timestamp'], filtered_df['eff'], label='Efficiency')
ax2.set_xlabel('Time')
ax2.set_ylabel('Efficiency')
ax2.set_title('Efficiency Over Time')
ax2.legend()
ax2.grid(True)

fig.autofmt_xdate()
fig.tight_layout()

output_image = os.path.splitext(filename)[0] + '_filtered_15-10-10_15-11-10.png'
fig.savefig(output_image, dpi=300, bbox_inches='tight')

plt.show()

print(f'Saved filtered figure to: {output_image}')