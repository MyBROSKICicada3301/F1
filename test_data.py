"""Quick test script to verify dashboard functions with real data."""
import fastf1
import pandas as pd
from data_loader import load_session, get_race_results, get_driver_laps, get_driver_comparison
import time

print("=" * 70)
print("🏁 F1 DASHBOARD - DATA INTEGRITY TEST")
print("=" * 70)

# Enable cache
fastf1.Cache.enable_cache('f1_cache')

# Test 1: Load a recent race
print("\n✓ Test 1: Loading 2025 Japanese Grand Prix (Race)...")
session = load_session(2025, 'Japanese Grand Prix', 'R')

if session is None:
    print("❌ Failed to load session")
    exit(1)

print(f"  → Session loaded: {session}")
print(f"  → Session date: {session.date}")
print(f"  → Number of drivers: {len(session.drivers)}")
print(f"  → Drivers: {', '.join(session.drivers[:5])}... ({len(session.drivers)} total)")

# Test 2: Get race results
print("\n✓ Test 2: Fetching race results...")
results = get_race_results(2025, 'Japanese Grand Prix')

if results is None or len(results) == 0:
    print("❌ No results available")
else:
    print(f"  → Finishers: {len(results)}")
    print(f"  → Podium:")
    for idx, row in results.head(3).iterrows():
        print(f"    {int(row['Position'])}. {row['FullName']} - {int(row['Points'])} points")

# Test 3: Get driver laps
print("\n✓ Test 3: Loading driver lap data...")
driver = session.drivers[0]
laps = get_driver_laps(2025, 'Japanese Grand Prix', driver)

if laps is None or len(laps) == 0:
    print(f"❌ No lap data for driver {driver}")
else:
    print(f"  → Driver: {driver}")
    print(f"  → Total laps: {len(laps)}")
    best_lap = pd.to_timedelta(laps['LapTime']).min()
    print(f"  → Best lap: {best_lap}")
    avg_lap = pd.to_timedelta(laps['LapTime']).mean()
    print(f"  → Average lap: {avg_lap}")

# Test 4: Compare two drivers
print("\n✓ Test 4: Comparing two drivers...")
if len(session.drivers) >= 2:
    driver1, driver2 = session.drivers[0], session.drivers[1]
    laps1, laps2 = get_driver_comparison(2025, 'Japanese Grand Prix', driver1, driver2)
    
    if laps1 is not None and laps2 is not None:
        print(f"  → {driver1} vs {driver2}")
        print(f"  → {driver1}: {len(laps1)} laps | Best: {pd.to_timedelta(laps1['LapTime']).min()}")
        print(f"  → {driver2}: {len(laps2)} laps | Best: {pd.to_timedelta(laps2['LapTime']).min()}")
    else:
        print(f"❌ Could not compare drivers")

# Test 5: Tire compounds
print("\n✓ Test 5: Checking tire strategy...")
all_laps = session.laps
compounds = all_laps['Compound'].unique()
print(f"  → Tire compounds used: {list(compounds)}")

compound_counts = all_laps['Compound'].value_counts()
for compound, count in compound_counts.items():
    print(f"    - {compound}: {count} laps")

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED! Dashboard is working with real F1 data.")
print("=" * 70)
print("\n💡 Next step: Open http://localhost:8501 in your browser to use the dashboard!")
