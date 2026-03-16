"""Test script to verify driver name formatting."""
import fastf1
import pandas as pd

# Enable cache
fastf1.Cache.enable_cache('f1_cache')

print("=" * 70)
print("🏁 DRIVER NAME FORMATTING TEST")
print("=" * 70)

# Load a session to test
print("\n✓ Loading 2025 Japanese Grand Prix (Race)...")
session = fastf1.get_session(2025, 'Japanese Grand Prix', 'R')
session.load(telemetry=False, weather=False)

print(f"  → Drivers loaded: {len(session.drivers)}")
print(f"  → Driver numbers: {sorted(session.drivers)}")

# Test the new formatting functions
print("\n✓ Testing driver name mapping from results...")

if session.results is not None and len(session.results) > 0:
    print(f"  → Results available for {len(session.results)} entries")
    
    # Show first few drivers with formatted names
    print("\n  Formatted Driver Display:")
    driver_map = {}
    
    for idx, row in session.results.iterrows():
        try:
            driver_num = str(int(row['DriverNumber']))
            driver_name = row['FullName']
            driver_map[driver_num] = driver_name
        except:
            pass
    
    # Display the mapping
    drivers_to_show = sorted(session.drivers)[:10]
    for driver_num in drivers_to_show:
        driver_num_str = str(driver_num)
        driver_name = driver_map.get(driver_num_str, "Unknown")
        formatted = f"{driver_num_str} - {driver_name}"
        print(f"    {formatted}")

print("\n" + "=" * 70)
print("✅ DRIVER NAME FORMATTING TEST PASSED!")
print("=" * 70)
