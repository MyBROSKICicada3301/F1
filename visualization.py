"""Visualization functions for Formula 1 data analysis and display."""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st
import numpy as np

# Configure visualization style for better readability
sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (12, 6)


def plot_top_finishers(results):
    """Display top 10 finishing positions with color-coding for podium places."""
    if results is None or len(results) == 0:
        st.warning("No results available to display")
        return
    
    top10 = results.head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['gold' if i < 3 else 'lightgray' for i in range(len(top10))]
    ax.barh(range(len(top10)), top10['Points'].values, color=colors)
    ax.set_yticks(range(len(top10)))
    ax.set_yticklabels([f"{int(pos)}. {name}" for pos, name in zip(top10['Position'], top10['FullName'])])
    ax.set_xlabel('Points')
    ax.set_title('Top 10 Finishers')
    ax.invert_yaxis()
    
    st.pyplot(fig)


def plot_lap_times(laps, driver_name):
    """Show how lap times changed throughout the race, indicating pace evolution."""
    if laps is None or len(laps) == 0:
        st.warning("No lap data available")
        return
    
    lap_times = pd.to_timedelta(laps['LapTime']).dt.total_seconds()
    fig, ax = plt.subplots(figsize=(12, 5))
    
    ax.plot(range(1, len(lap_times) + 1), lap_times, marker='o', linewidth=2, markersize=6, color='#1f77b4')
    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Lap Time (seconds)')
    ax.set_title(f'{driver_name} - Lap Time Progression')
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)


def plot_sector_times(laps, driver_name):
    """Analyze sector-by-sector performance to identify strengths and weaknesses."""
    if laps is None or len(laps) == 0:
        st.warning("No lap data available")
        return
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    sector1 = pd.to_timedelta(laps['Sector1Time']).dt.total_seconds()
    sector2 = pd.to_timedelta(laps['Sector2Time']).dt.total_seconds()
    sector3 = pd.to_timedelta(laps['Sector3Time']).dt.total_seconds()
    
    x = np.arange(len(sector1))
    width = 0.25
    
    ax.bar(x - width, sector1, width, label='Sector 1', alpha=0.8)
    ax.bar(x, sector2, width, label='Sector 2', alpha=0.8)
    ax.bar(x + width, sector3, width, label='Sector 3', alpha=0.8)
    
    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Time (seconds)')
    ax.set_title(f'{driver_name} - Sector Times by Lap')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    st.pyplot(fig)


def plot_driver_comparison(laps1, laps2, driver1, driver2, driver_names_map=None):
    """Compare lap times of two drivers."""
    if laps1 is None or laps2 is None:
        st.warning("Could not load data for one or both drivers")
        return
    
    # Format driver names
    from data_loader import format_driver_name
    if driver_names_map is None:
        driver_names_map = {}
    
    driver1_label = format_driver_name(driver1, driver_names_map)
    driver2_label = format_driver_name(driver2, driver_names_map)
    
    times1 = pd.to_timedelta(laps1['LapTime']).dt.total_seconds()
    times2 = pd.to_timedelta(laps2['LapTime']).dt.total_seconds()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(range(1, len(times1) + 1), times1, marker='o', label=driver1_label, linewidth=2, markersize=5)
    ax.plot(range(1, len(times2) + 1), times2, marker='s', label=driver2_label, linewidth=2, markersize=5)
    
    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Lap Time (seconds)')
    ax.set_title(f'{driver1_label} vs {driver2_label} - Lap Time Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)


def plot_telemetry(telemetry, lap_desc):
    """Visualize speed and throttle application data across the lap distance."""
    if telemetry is None or len(telemetry) == 0:
        st.warning("No telemetry data available")
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Speed plot
    distance = telemetry['Distance'].values
    speed = telemetry['Speed'].values
    ax1.plot(distance, speed, label='Speed', color='red', linewidth=1.5)
    ax1.fill_between(distance, speed, alpha=0.3, color='red')
    ax1.set_ylabel('Speed (km/h)')
    ax1.set_title(f'{lap_desc} - Telemetry Data')
    ax1.grid(True, alpha=0.3)
    
    # Throttle plot
    throttle = telemetry['Throttle'].values
    ax2.plot(distance, throttle, label='Throttle', color='green', linewidth=1.5)
    ax2.fill_between(distance, throttle, alpha=0.3, color='green')
    ax2.set_xlabel('Distance (m)')
    ax2.set_ylabel('Throttle (%)')
    ax2.grid(True, alpha=0.3)
    
    st.pyplot(fig)


def plot_tire_degradation(laps, driver_name):
    """Show how tires lost performance over consecutive laps for each compound."""
    if laps is None or len(laps) == 0:
        st.warning("No lap data available")
        return
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Group by tire compound
    soft_laps = laps[laps['Compound'] == 'SOFT']
    medium_laps = laps[laps['Compound'] == 'MEDIUM']
    hard_laps = laps[laps['Compound'] == 'HARD']
    
    if len(soft_laps) > 0:
        soft_times = pd.to_timedelta(soft_laps['LapTime']).dt.total_seconds()
        ax.plot(range(len(soft_times)), soft_times, marker='o', label='Soft', linewidth=2)
    
    if len(medium_laps) > 0:
        med_times = pd.to_timedelta(medium_laps['LapTime']).dt.total_seconds()
        ax.plot(range(len(med_times)), med_times, marker='s', label='Medium', linewidth=2)
    
    if len(hard_laps) > 0:
        hard_times = pd.to_timedelta(hard_laps['LapTime']).dt.total_seconds()
        ax.plot(range(len(hard_times)), hard_times, marker='^', label='Hard', linewidth=2)
    
    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Lap Time (seconds)')
    ax.set_title(f'{driver_name} - Tire Degradation')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)
