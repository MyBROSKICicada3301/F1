"""
Formula 1 Interactive Dashboard
A comprehensive analytical tool for exploring historical Formula 1 races,
driver performance analysis, and telemetry data.
"""
import streamlit as st
import pandas as pd
import fastf1
from data_loader import (
    load_session, get_race_results, get_driver_laps, 
    get_driver_comparison, get_lap_telemetry, get_track_status,
    get_driver_names_map, format_driver_name
)
from visualization import (
    plot_top_finishers, plot_lap_times, plot_sector_times,
    plot_driver_comparison, plot_telemetry, plot_tire_degradation
)
from race_visualizer import (
    plot_position_changes_over_race, plot_fastest_lap_comparison,
    plot_driver_lap_comparison, plot_speed_heatmap_by_driver,
    plot_lap_time_distribution, plot_dynamic_track_animation,
    plot_multi_driver_race_animation,
    plot_live_track_position_animation
)
from utils import get_seasons, get_events, format_time_detailed

# Page config
st.set_page_config(page_title="F1 Dashboard", layout="wide")

st.title("Formula 1 Interactive Dashboard")
st.markdown("Explore historical Formula 1 race data, telemetry, and driver performance comparisons.")

# Sidebar navigation menu
st.sidebar.markdown("## Navigation")
page = st.sidebar.radio("Available Views:", [
    "Race Results",
    "Driver Analysis",
    "Driver Comparison",
    "Lap Telemetry",
    "Race Visualizer",
    "Tire Strategy"
])

# Common race and event selection interface
st.sidebar.markdown("---")
st.sidebar.markdown("## Select Race")

season = st.sidebar.selectbox("Season:", get_seasons()[::-1])  # Latest first
events = get_events(season)

if not events:
    st.error(f"No events found for season {season}. Please try another year.")
    st.stop()

event = st.sidebar.selectbox("Grand Prix:", events)
session_type = st.sidebar.selectbox("Session:", ["R", "Q", "FP3", "FP2", "FP1"], format_func=lambda x: {"R": "Race", "Q": "Qualifying", "FP3": "FP3", "FP2": "FP2", "FP1": "FP1"}[x])

# Load session data
with st.spinner(f"Loading {season} {event} ({session_type})..."):
    session = load_session(season, event, session_type)

if session is None:
    st.error("Failed to load session data.")
    st.stop()

# Check if session has drivers (no valid data)
if len(session.drivers) == 0:
    st.error(f"No race data available for {season} {event}. This session may not have occurred yet or data is unavailable on FastF1.")
    st.info("Tip: Select a season from 2019-2025 and a completed race.")
    st.stop()

# Get driver names mapping for display
driver_names_map = get_driver_names_map(season, event)
# Helper function to format driver display
def get_driver_label(driver_num):
    return format_driver_name(driver_num, driver_names_map)

# Display race results and podium information
if page == "Race Results":
    st.header(f"Race Results - {season} {event}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Top 10 Finishers")
        results = get_race_results(season, event)
        if results is not None:
            st.dataframe(results, use_container_width=True)
            plot_top_finishers(results)
    
    with col2:
        st.subheader("Race Stats")
        if results is not None:
            st.metric("Total Finishers", len(results))
            st.metric("Podium Position 1", results.iloc[0]['FullName'] if len(results) > 0 else "N/A")
            st.metric("Podium Position 2", results.iloc[1]['FullName'] if len(results) > 1 else "N/A")
            st.metric("Podium Position 3", results.iloc[2]['FullName'] if len(results) > 2 else "N/A")

# Detailed driver performance analysis across the race
elif page == "Driver Analysis":
    st.header(f"Driver Analysis - {season} {event}")
    
    drivers = sorted(session.drivers)
    driver = st.selectbox("Select Driver:", drivers, format_func=get_driver_label)
    
    if driver:
        with st.spinner(f"Loading {driver}'s data..."):
            laps = get_driver_laps(season, event, driver)
        
        if laps is not None and len(laps) > 0:
            st.subheader(f"{format_driver_name(driver, driver_names_map)} - Race Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Laps", len(laps))
            with col2:
                best_lap = pd.to_timedelta(laps['LapTime']).min()
                st.metric("Best Lap", f"{int(best_lap.total_seconds() // 60)}:{best_lap.total_seconds() % 60:06.3f}")
            with col3:
                avg_lap = pd.to_timedelta(laps['LapTime']).mean()
                st.metric("Avg Lap", f"{int(avg_lap.total_seconds() // 60)}:{avg_lap.total_seconds() % 60:06.3f}")
            with col4:
                st.metric("Pit Stops", len(laps[laps['PitOutTime'].notna()]))
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Lap Time Progression")
                plot_lap_times(laps, format_driver_name(driver, driver_names_map))
            
            with col2:
                st.subheader("Sector Times")
                plot_sector_times(laps, format_driver_name(driver, driver_names_map))
            
            st.subheader("Tire Degradation")
            plot_tire_degradation(laps, format_driver_name(driver, driver_names_map))
        
        else:
            st.warning(f"No lap data available for {format_driver_name(driver, driver_names_map)} in this session.")

# Compare performance metrics between two drivers
elif page == "Driver Comparison":
    st.header(f"Driver Comparison - {season} {event}")
    
    drivers = sorted(session.drivers)
    
    col1, col2 = st.columns(2)
    with col1:
        driver1 = st.selectbox("Driver 1:", drivers, key="driver1", format_func=get_driver_label)
    with col2:
        driver2 = st.selectbox("Driver 2:", drivers, key="driver2", index=1 if len(drivers) > 1 else 0, format_func=get_driver_label)
    
    if driver1 and driver2 and driver1 != driver2:
        with st.spinner(f"Loading {driver1} vs {driver2}..."):
            laps1, laps2 = get_driver_comparison(season, event, driver1, driver2)
        
        if laps1 is not None and laps2 is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                best1 = pd.to_timedelta(laps1['LapTime']).min()
                st.metric(f"{format_driver_name(driver1, driver_names_map)} Best Lap", f"{int(best1.total_seconds() // 60)}:{best1.total_seconds() % 60:06.3f}")
            
            with col2:
                best2 = pd.to_timedelta(laps2['LapTime']).min()
                st.metric(f"{format_driver_name(driver2, driver_names_map)} Best Lap", f"{int(best2.total_seconds() // 60)}:{best2.total_seconds() % 60:06.3f}")
            
            st.markdown("---")
            st.subheader("Lap Time Comparison")
            plot_driver_comparison(laps1, laps2, driver1, driver2, driver_names_map)
            
            # Detailed comparison table
            st.subheader("Lap-by-Lap Details")
            
            # Handle cases where drivers have different numbers of laps
            max_laps = max(len(laps1), len(laps2))
            comparison_data = {
                f"{format_driver_name(driver1, driver_names_map)} Lap Time": list(laps1['LapTime'].values) + [None] * (max_laps - len(laps1)),
                f"{format_driver_name(driver2, driver_names_map)} Lap Time": list(laps2['LapTime'].values) + [None] * (max_laps - len(laps2)),
            }
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True)

# Display detailed telemetry data including speed and throttle profiles
elif page == "Lap Telemetry":
    st.header(f"Lap Telemetry - {season} {event}")
    
    drivers = sorted(session.drivers)
    driver = st.selectbox("Select Driver:", drivers, format_func=get_driver_label)
    
    if driver:
        laps = get_driver_laps(season, event, driver)
        if laps is not None and len(laps) > 0:
            lap_number = st.slider("Select Lap:", 1, len(laps), 1)
            
            with st.spinner("Loading telemetry data..."):
                telemetry = get_lap_telemetry(season, event, driver, lap_number)
            
            if telemetry is not None:
                st.subheader(f"{format_driver_name(driver, driver_names_map)} - Lap {lap_number} Telemetry")
                plot_telemetry(telemetry, f"{format_driver_name(driver, driver_names_map)} Lap {lap_number}")
                
                # Telemetry stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Max Speed", f"{telemetry['Speed'].max():.0f} km/h")
                with col2:
                    st.metric("Avg Speed", f"{telemetry['Speed'].mean():.0f} km/h")
                with col3:
                    st.metric("Distance", f"{telemetry['Distance'].max() / 1000:.2f} km")

# Watch drivers move around the track with position tracking throughout the race
elif page == "Race Visualizer":
    st.header(f"Race Visualizer - {season} {event}")
    st.markdown("Analyze driver positions and performance throughout the race using real track coordinates.")
    
    # Tab selection for different visualizations
    viz_tab1, viz_tab2, viz_tab3, viz_tab4, viz_tab5, viz_tab6, viz_tab7 = st.tabs([
        "Position Changes Over Race",
        "Fastest Lap Analysis",
        "Driver Comparison",
        "Speed Heatmaps",
        "Lap Time Distribution",
        "Single Driver Fastest Lap Animation",
        "Multi-Driver Animation",
    ])
    
    with viz_tab1:
        st.subheader("Position Progression Throughout Race")
        st.markdown("View how each driver's position changed from lap to lap throughout the race.")
        plot_position_changes_over_race(session, driver_names_map)
    
    with viz_tab2:
        st.subheader("Fastest Lap Track Map")
        st.markdown("See the fastest lap of the race overlaid on the actual track with speed data at each point.")
        plot_fastest_lap_comparison(session, driver_names_map)
    
    with viz_tab3:
        st.subheader("Compare Two Drivers' Best Laps")
        st.markdown("Select two drivers to compare their best laps on the same track.")
        
        col1, col2 = st.columns(2)
        with col1:
            driver1 = st.selectbox("Driver 1:", [d for d in session.drivers], format_func=lambda d: get_driver_label(d))
        with col2:
            driver2 = st.selectbox("Driver 2:", [d for d in session.drivers if d != driver1], format_func=lambda d: get_driver_label(d))
        
        if driver1 and driver2:
            plot_driver_lap_comparison(session, driver1, driver2, driver_names_map)
    
    with viz_tab4:
        st.subheader("Speed Distribution Heatmaps")
        st.markdown("View speed profiles for the top 12 drivers' best laps across the track.")
        plot_speed_heatmap_by_driver(session, driver_names_map, num_drivers=12)
    
    with viz_tab5:
        st.subheader("Lap Time Consistency Analysis")
        st.markdown("Analyze lap time distribution and consistency for the top 10 drivers.")
        plot_lap_time_distribution(session, driver_names_map)
    
    with viz_tab6:
        st.subheader("Dynamic Single Driver Animation")
        st.markdown("Watch a selected driver navigate around the track with live speed and position data.")
        
        drivers = sorted(session.drivers)
        selected_driver = st.selectbox("Select Driver to Animate:", drivers, format_func=get_driver_label, key="anim_driver")
        frame_skip = st.slider("Animation Speed (lower = faster):", 1, 20, 5)
        
        if selected_driver:
            with st.spinner(f"Creating animation for {get_driver_label(selected_driver)}..."):
                plot_dynamic_track_animation(session, selected_driver, driver_names_map, frame_skip=frame_skip)
    
    with viz_tab7:
        st.subheader("Multi-Driver Race Animation")
        st.markdown("Watch multiple drivers race simultaneously, comparing their fastest laps.")
        
        drivers = sorted(session.drivers)
        selected_drivers = st.multiselect(
            "Select Drivers to Compare:",
            drivers,
            format_func=get_driver_label,
            default=drivers[:3] if len(drivers) >= 3 else drivers
        )
        frame_skip = st.slider("Animation Speed (lower = faster):", 1, 20, 10, key="multi_frame_skip")
        
        if selected_drivers and len(selected_drivers) > 0:
            with st.spinner(f"Creating animation for {len(selected_drivers)} drivers..."):
                plot_multi_driver_race_animation(session, selected_drivers, driver_names_map, frame_skip=frame_skip)

# Analyze tire compound usage and degradation patterns throughout the race
elif page == "Tire Strategy":
    st.header(f"Tire Strategy Analysis - {season} {event}")
    
    st.subheader("Race Tire Compounds by Driver")
    
    drivers = sorted(session.drivers)
    driver_laps = {}
    tire_data = []
    
    for driver in drivers:
        laps = get_driver_laps(season, event, driver)
        if laps is not None and len(laps) > 0:
            for idx, lap in laps.iterrows():
                tire_data.append({
                    'Driver': driver,
                    'Lap': lap['LapNumber'],
                    'Compound': lap['Compound'],
                    'LapTime': lap['LapTime'],
                    'TyreLife': lap['TyreLife']
                })
    
    if tire_data:
        tire_df = pd.DataFrame(tire_data)
        
        # Format driver names in tire_df for display
        tire_df['DriverDisplay'] = tire_df['Driver'].apply(get_driver_label)
        
        # Tire compound summary
        summary = tire_df.groupby(['DriverDisplay', 'Compound']).size().unstack(fill_value=0)
        st.subheader("Tires Used by Driver")
        st.dataframe(summary, use_container_width=True)
        
        # Visualize tire strategy
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        fig, ax = plt.subplots(figsize=(14, 6))
        for driver in drivers[:10]:  # Top 10 drivers to avoid overcrowding
            data = tire_df[tire_df['Driver'] == driver]
            if len(data) > 0:
                driver_label = get_driver_label(driver)
                ax.scatter(data['Lap'], data['TyreLife'], label=driver_label, s=50, alpha=0.6)
        
        ax.set_xlabel('Lap Number')
        ax.set_ylabel('Tyre Age (Laps)')
        ax.set_title('Tire Age Progression - Top 10 Drivers')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

st.sidebar.markdown("---")
st.sidebar.markdown("Data provided by FastF1 | Built with Streamlit and Python")
