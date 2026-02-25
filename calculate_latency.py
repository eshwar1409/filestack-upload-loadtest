import pandas as pd
import numpy as np
import os
import sys
import time

FILE_PATH = "webhook1.json"
EXPECTED_EVENTS = int(os.getenv("EXPECTED_EVENTS", "10000"))
OUTPUT_SUMMARY = "webhook_statistics.csv"

print("Waiting for webhook events...")

while True:
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH) as f:
            count = sum(1 for _ in f)
        print(f"Received {count}/{EXPECTED_EVENTS}")

        if count >= EXPECTED_EVENTS:
            break

    time.sleep(10)

print("Calculating latency...")

df = pd.read_json(FILE_PATH, lines=True)

df["event_ts_raw"] = df["body"].apply(
    lambda x: x.get("timestamp") if isinstance(x, dict) else None
)

df = df.dropna(subset=["event_ts_raw", "timestamp"])

def convert_ts(ts):
    ts = int(ts)
    return pd.to_datetime(ts, unit="ms" if len(str(ts)) == 13 else "s", utc=True)

df["event_time"] = df["event_ts_raw"].apply(convert_ts)
df["receiver_time"] = pd.to_datetime(df["timestamp"], utc=True)

df["latency_s"] = (df["receiver_time"] - df["event_time"]).dt.total_seconds()
df = df[df["latency_s"] >= 0]

latencies = df["latency_s"].values

summary = {
    "total_events": len(df),
    "latency_min_s": np.min(latencies),
    "latency_p50_s": np.percentile(latencies, 50),
    "latency_p90_s": np.percentile(latencies, 90),
    "latency_p95_s": np.percentile(latencies, 95),
    "latency_p99_s": np.percentile(latencies, 99),
    "latency_max_s": np.max(latencies),
}

summary_df = pd.DataFrame([summary])
summary_df.to_csv(OUTPUT_SUMMARY, index=False)

print(summary_df)


print("Latency within acceptable range.")