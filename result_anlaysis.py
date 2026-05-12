import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os

# ===== CONFIG SECTION =====
# 15-10-10 to 15-11-10: 10s short-term stability test
# 15-10-53 to 15-24-52: 10min short term stability test
# 15-30-30 to 16-40-00: 1hr long term stability test

#filename = "20260512_Efficiency_longterm_1hr.txt"
filename = "20260512_Efficiency_shortterm_10s_m_.txt"
start_time = datetime.time(15, 10, 10)
end_time = datetime.time(15, 11, 10)
dpi = 300
figsize1 = (12, 8)
figsize2 = (12, 6)
x_axis_interval_minutes = 0.1  # X-axis time interval in minutes
first_window_minutes = .1  # average on the first N minutes of filtered data
middle_window_minutes = .1  # average on the middle N minutes of filtered data
last_window_minutes = .1   # average on the last N minutes of filtered data
# =======================

df = pd.read_csv(filename, sep=';')

df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Seoul')

for col in ['p_in', 'p_out', 'eff', 'temperature', 'temperature_room']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# KST filtering
filtered_df = df[
    (df['timestamp'].dt.time >= start_time) &
    (df['timestamp'].dt.time <= end_time)
].copy()

print(f'Full rows: {len(df)}, filtered rows: {len(filtered_df)}')
print(f'Available local time range: {df["timestamp"].min()} - {df["timestamp"].max()}')

if filtered_df.empty:
    raise ValueError("filtered_df is empty. Check start_time and end_time.")

# Average efficiency for the first, middle, and last windows
first_window_end = filtered_df['timestamp'].min() + datetime.timedelta(minutes=first_window_minutes)
last_window_start = filtered_df['timestamp'].max() - datetime.timedelta(minutes=last_window_minutes)
center_time = filtered_df['timestamp'].min() + (filtered_df['timestamp'].max() - filtered_df['timestamp'].min()) / 2
middle_window_half = datetime.timedelta(minutes=middle_window_minutes / 2)
middle_window_start = center_time - middle_window_half
middle_window_end = center_time + middle_window_half
first_avg_eff = filtered_df[filtered_df['timestamp'] <= first_window_end]['eff'].mean()
middle_avg_eff = filtered_df[(filtered_df['timestamp'] >= middle_window_start) & (filtered_df['timestamp'] <= middle_window_end)]['eff'].mean()
last_avg_eff = filtered_df[filtered_df['timestamp'] >= last_window_start]['eff'].mean()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize1, sharex=True)

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

avg_text = (
    f'First {first_window_minutes:.1f} min avg: {first_avg_eff:.3f}\n'
    f'Middle {middle_window_minutes:.1f} min avg: {middle_avg_eff:.3f}\n'
    f'Last {last_window_minutes:.1f} min avg: {last_avg_eff:.3f}'
)
ax2.text(
    0.02,
    0.95,
    avg_text,
    transform=ax2.transAxes,
    verticalalignment='top',
    bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray')
)

# Set x-axis time interval
from datetime import timedelta
interval_delta = timedelta(minutes=x_axis_interval_minutes)
times = []
current = filtered_df['timestamp'].min()
while current <= filtered_df['timestamp'].max():
    times.append(current)
    current += interval_delta
ax1.set_xticks(times)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

fig.autofmt_xdate()
fig.tight_layout()

output_image = os.path.splitext(filename)[0] + f'_filtered_{start_time.strftime("%H-%M-%S")}_{end_time.strftime("%H-%M-%S")}.png'
fig.savefig(output_image, dpi=dpi, bbox_inches='tight')
print(f'Saved filtered figure to: {output_image}')

# Second figure: Temperature overlay
fig2, ax3 = plt.subplots(figsize=figsize2)
ax3.plot(filtered_df['timestamp'], filtered_df['temperature'], label='Board Temp (°C)', color='orange')
ax3.plot(filtered_df['timestamp'], filtered_df['temperature_room'], label='Room Temp (°C)', color='purple')
ax3.set_xlabel('Time')
ax3.set_ylabel('Temperature (°C)')
ax3.set_title('Board and Room Temperature Over Time (Filtered)')
ax3.legend()
ax3.grid(True)

# Set x-axis time interval
ax3.set_xticks(times)
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

fig2.autofmt_xdate()
fig2.tight_layout()

output_image2 = os.path.splitext(filename)[0] + f'_temperature_overlay_{start_time.strftime("%H-%M-%S")}_{end_time.strftime("%H-%M-%S")}.png'
fig2.savefig(output_image2, dpi=dpi, bbox_inches='tight')
print(f'Saved temperature figure to: {output_image2}')

plt.show()
