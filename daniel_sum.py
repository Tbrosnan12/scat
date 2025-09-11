import sys
import pandas as pd

file=sys.argv[1]

# Load your CSV
df = pd.read_csv(file)

# Group by site (collapsing detectors)
site_agg = df.groupby(
    ["End_Time", "Region", "Site"], as_index=False
).agg(
    Sum_Volume=("Sum_Volume", "sum"),
    Avg_Volume=("Avg_Volume", "mean")
)


# Create output filename based on input
import os
basename = os.path.splitext(os.path.basename(file))[0]  # strip directory and .csv
outname = f"{basename}_collapsed.csv"
# Save to new CSV
site_agg.to_csv(outname, index=False)
print(f"Saved: {outname}")
print(site_agg.head())
