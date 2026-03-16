"""
Race visualization tools for displaying driver positions and lap progression.
Uses FastF1's native plotting functions for accurate track map visualization.
"""
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import numpy as np
import fastf1.plotting as plotting
from utils import format_time_detailed


def plot_position_changes_over_race(session, driver_names_map=None):
    """
    Show how drivers' positions changed throughout the race.
    Displays line plot of position changes for each driver.
    """
    if session is None or session.laps is None:
        st.warning("No session data available")
        return
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Get position data for each driver
    drivers = session.drivers
    colors = plt.cm.tab20(np.linspace(0, 1, len(drivers)))
    
    try:
        for idx, driver in enumerate(drivers[:15]):  # Limit to top 15 to avoid clutter
            driver_laps = session.laps.pick_drivers(driver)
            
            if len(driver_laps) > 0:
                laps = driver_laps['LapNumber'].values
                positions = driver_laps['Position'].values
                
                # Filter out NaN positions
                valid_idx = ~pd.isna(positions)
                
                if valid_idx.sum() > 0:
                    label = f"{driver} - {driver_names_map.get(str(driver), 'Unknown')}" if driver_names_map else driver
                    ax.plot(laps[valid_idx], positions[valid_idx], 
                           marker='o', markersize=4, color=colors[idx], label=label, linewidth=1.5)
    
        ax.set_xlabel('Lap Number', fontsize=12)
        ax.set_ylabel('Position', fontsize=12)
        ax.set_title('Driver Position Changes Throughout Race', fontsize=14, fontweight='bold')
        ax.invert_yaxis()  # Invert so position 1 is at top
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        ax.set_ylim(len(drivers) + 1, 0)
        
        fig.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error creating position chart: {str(e)}")


def plot_fastest_lap_comparison(session, driver_names_map=None):
    """
    Plot fastest lap track map with corner annotations for speed data.
    Shows corner speeds and identifies high-speed and low-speed sections.
    """
    if session is None:
        st.warning("No session data available")
        return
    
    try:
        # Find the fastest lap across all drivers
        laps = session.laps.copy()
        
        # Get laps with valid lap times
        laps = laps[laps['LapTime'].notna()]
        
        if len(laps) == 0:
            st.warning("No valid lap times available")
            return
        
        # Find fastest lap
        fastest_lap = laps.loc[laps['LapTime'].idxmin()]
        fastest_driver = fastest_lap['Driver']
        
        # Load telemetry for the fastest lap
        try:
            lap_telemetry = fastest_lap.get_telemetry()
        except:
            st.warning("Could not load telemetry for fastest lap")
            return
        
        if lap_telemetry is None or len(lap_telemetry) == 0:
            st.warning("No telemetry data available for fastest lap")
            return
        
        # Create figure with track map
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot the track map
        plotting.plot_track(session, ax=ax, track_width=0.5, color='black')
        
        # Plot lap data as scatter with color based on speed
        scatter = ax.scatter(lap_telemetry['X'], lap_telemetry['Y'], 
                           c=lap_telemetry['Speed'], 
                           cmap='RdYlGn', 
                           s=5, 
                           alpha=0.8)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Speed (km/h)', fontsize=12)
        
        driver_label = f"{fastest_driver} - {driver_names_map.get(str(fastest_driver), 'Unknown')}" if driver_names_map else fastest_driver
        lap_time = fastest_lap['LapTime']
        
        ax.set_title(f'Fastest Lap Track Map - {driver_label}\nLap Time: {lap_time}', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Distance (m)')
        ax.set_ylabel('Distance (m)')
        
        st.pyplot(fig)
        
    except Exception as e:
        st.error(f"Error creating lap comparison plot: {str(e)}")


def plot_driver_lap_comparison(session, driver1, driver2, driver_names_map=None):
    """
    Compare track maps of two drivers' best laps.
    Shows both laps on the same track with different colors.
    """
    if session is None:
        st.warning("No session data available")
        return
    
    try:
        # Get fastest lap for each driver
        laps1 = session.laps.pick_drivers(driver1)
        laps2 = session.laps.pick_drivers(driver2)
        
        if len(laps1) == 0 or len(laps2) == 0:
            st.warning("Could not find valid laps for both drivers")
            return
        
        fastest_lap1 = laps1.loc[laps1['LapTime'].idxmin()]
        fastest_lap2 = laps2.loc[laps2['LapTime'].idxmin()]
        
        # Get telemetry
        try:
            telemetry1 = fastest_lap1.get_telemetry()
            telemetry2 = fastest_lap2.get_telemetry()
        except:
            st.warning("Could not load telemetry for comparison")
            return
        
        if telemetry1 is None or telemetry2 is None:
            st.warning("Telemetry data unavailable")
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot track
        plotting.plot_track(session, ax=ax, track_width=0.5, color='gray', alpha=0.3)
        
        # Plot both laps with different colors
        ax.plot(telemetry1['X'], telemetry1['Y'], 
               color='#1f77b4', linewidth=2, alpha=0.8, 
               label=f"{driver1} - {fastest_lap1['LapTime']}")
        
        ax.plot(telemetry2['X'], telemetry2['Y'], 
               color='#ff7f0e', linewidth=2, alpha=0.8, 
               label=f"{driver2} - {fastest_lap2['LapTime']}")
        
        driver_label1 = f"{driver1} - {driver_names_map.get(str(driver1), 'Unknown')}" if driver_names_map else driver1
        driver_label2 = f"{driver2} - {driver_names_map.get(str(driver2), 'Unknown')}" if driver_names_map else driver2
        
        ax.set_title(f'Driver Lap Comparison: {driver_label1} vs {driver_label2}', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Distance (m)')
        ax.set_ylabel('Distance (m)')
        ax.legend(fontsize=11)
        
        st.pyplot(fig)
        
    except Exception as e:
        st.error(f"Error comparing driver laps: {str(e)}")


def plot_speed_heatmap_by_driver(session, driver_names_map=None, num_drivers=12):
    """
    Create a heatmap showing speed distribution for top drivers.
    Darker colors indicate higher speeds.
    """
    if session is None or session.laps is None:
        st.warning("No session data available")
        return
    
    try:
        drivers = session.drivers[:num_drivers]
        
        fig, axes = plt.subplots(3, 4, figsize=(16, 12))
        axes = axes.flatten()
        
        for idx, driver in enumerate(drivers):
            ax = axes[idx]
            
            try:
                driver_laps = session.laps.pick_drivers(driver)
                
                if len(driver_laps) > 0:
                    # Get the fastest lap for this driver
                    fastest_lap = driver_laps.loc[driver_laps['LapTime'].idxmin()]
                    telemetry = fastest_lap.get_telemetry()
                    
                    if telemetry is not None and len(telemetry) > 0:
                        # Plot track
                        plotting.plot_track(session, ax=ax, track_width=0.3, color='gray', alpha=0.2)
                        
                        # Plot speed data
                        scatter = ax.scatter(telemetry['X'], telemetry['Y'], 
                                           c=telemetry['Speed'], 
                                           cmap='RdYlGn', 
                                           s=3, 
                                           alpha=0.8)
                        
                        driver_label = f"{driver} - {driver_names_map.get(str(driver), 'Unknown')}" if driver_names_map else driver
                        ax.set_title(driver_label, fontsize=10)
                        ax.set_xticks([])
                        ax.set_yticks([])
            
            except Exception as e:
                ax.text(0.5, 0.5, f"Error loading data", 
                       ha='center', va='center', transform=ax.transAxes)
        
        # Hide unused subplots
        for idx in range(len(drivers), len(axes)):
            axes[idx].set_visible(False)
        
        fig.suptitle('Driver Speed Heatmaps - Fastest Laps', fontsize=14, fontweight='bold')
        fig.tight_layout()
        st.pyplot(fig)
        
    except Exception as e:
        st.error(f"Error creating speed heatmap: {str(e)}")


def plot_lap_time_distribution(session, driver_names_map=None):
    """
    Show distribution of lap times for each driver.
    Identifies consistency and performance variation.
    """
    if session is None or session.laps is None:
        st.warning("No session data available")
        return
    
    try:
        fig, ax = plt.subplots(figsize=(14, 6))
        
        drivers = session.drivers[:10]  # Top 10 drivers
        
        lap_time_data = []
        labels = []
        
        for driver in drivers:
            driver_laps = session.laps.pick_drivers(driver)
            
            if len(driver_laps) > 0:
                lap_times = pd.to_timedelta(driver_laps['LapTime']).dt.total_seconds()
                
                # Filter out NaN and pit laps
                lap_times = lap_times[~pd.isna(lap_times)]
                
                if len(lap_times) > 0:
                    lap_time_data.append(lap_times.values)
                    driver_label = f"{driver} - {driver_names_map.get(str(driver), 'Unknown')}" if driver_names_map else driver
                    labels.append(driver_label)
        
        if lap_time_data:
            bp = ax.boxplot(lap_time_data, labels=labels, patch_artist=True)
            
            # Color the boxes
            for patch in bp['boxes']:
                patch.set_facecolor('lightblue')
            
            ax.set_ylabel('Lap Time (seconds)', fontsize=12)
            ax.set_title('Lap Time Distribution by Driver', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            plt.xticks(rotation=45, ha='right')
            
            fig.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("No valid lap data available")
    
    except Exception as e:
        st.error(f"Error creating lap time distribution: {str(e)}")


def plot_sector_heatmap_by_driver(session, driver_names_map=None):
    """
    Create a heatmap showing sector times for each driver across all laps.
    Darker colors indicate faster sector times.
    """
    if session is None or session.laps is None:
        st.warning("No session data available")
        return
    
    # Prepare data
    drivers = session.drivers[:12]  # Top 12 drivers to keep readable
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    
    for sector_num, ax in enumerate(axes, 1):
        sector_col = f'Sector{sector_num}Time'
        
        # Collect sector times for drivers
        sector_matrix = []
        driver_labels = []
        
        for driver in drivers:
            driver_laps = session.laps.pick_drivers(driver)
            sector_times = pd.to_timedelta(driver_laps[sector_col]).dt.total_seconds()
            sector_matrix.append(sector_times.values)
            
            label = f"{driver} - {driver_names_map.get(str(driver), 'Unknown')}" if driver_names_map else driver
            driver_labels.append(label)
        
        # Find min and max for colormap  
        all_times = np.concatenate([s[~np.isnan(s)] for s in sector_matrix])
        vmin, vmax = all_times.min(), all_times.max()
        
        # Create heatmap
        im = ax.imshow(sector_matrix, cmap='RdYlGn_r', aspect='auto', vmin=vmin, vmax=vmax)
        ax.set_ylabel('Driver')
        ax.set_xlabel('Lap Number')
        ax.set_title(f'Sector {sector_num} Times Heatmap')
        ax.set_yticks(range(len(driver_labels)))
        ax.set_yticklabels(driver_labels, fontsize=9)
        
        plt.colorbar(im, ax=ax, label='Time (seconds)')
    
    fig.tight_layout()
    st.pyplot(fig)
