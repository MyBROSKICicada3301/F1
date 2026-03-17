"""
Race visualization tools for displaying driver positions and lap progression.
Uses FastF1's native plotting functions for accurate track map visualization.
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import streamlit as st
import numpy as np
import fastf1.plotting as plotting
from utils import format_time_detailed
from matplotlib.animation import PillowWriter
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import Circle
import io
import tempfile
import os


# Team colors mapping for F1 teams (official 2024 season colors)
TEAM_COLORS = {
    'Ferrari': '#DC0000',           # Red
    'Red Bull': '#00008F',          # Dark Blue
    'Mercedes': '#E8E8E8',          # Silver
    'McLaren': '#FF8700',           # Orange
    'Aston Martin': '#00644B',      # Green
    'Alpine': '#0082FA',            # Blue
    'Williams': '#005AFF',          # Blue
    'Haas': '#FFFFFF',              # White
    'Sauber': '#00644B',            # Green
    'RB': '#00008F',                # Dark Blue
}

# Driver number to team mapping (2024 season)
DRIVER_TEAMS = {
    1: 'Red Bull', 11: 'Red Bull',              # Verstappen, Perez
    44: 'Mercedes', 63: 'Mercedes',             # Hamilton, Russell
    16: 'Ferrari', 55: 'Ferrari',               # Leclerc, Sainz
    81: 'McLaren', 4: 'McLaren',                # Norris, Piastri
    14: 'Aston Martin', 18: 'Aston Martin',     # Alonso, Stroll
    31: 'Alpine', 9: 'Alpine',                  # Ocon, Gasly
    24: 'Williams', 2: 'Williams',              # Zhou, Sargeant
    22: 'RB', 45: 'RB',                         # Tsunoda, Ricciardo
    20: 'Haas', 27: 'Haas',                     # Magnussen, Hulkenberg
    99: 'Sauber', 77: 'Sauber',                 # Sauber team drivers
}


def get_driver_team_color(driver_number):
    """Get team color for a driver"""
    team = DRIVER_TEAMS.get(driver_number, 'Default')
    return TEAM_COLORS.get(team, '#808080')


def get_driver_initials(session, driver_number):
    """Get driver initials or number"""
    try:
        driver_info = session.get_driver(driver_number)
        if driver_info and hasattr(driver_info, 'short_name'):
            initials = driver_info.short_name[:3].upper()
            return initials
    except:
        pass
    return str(driver_number)


def create_driver_marker_text(driver_number, initials=''):
    """Create marker text (driver number or initials)"""
    if initials and len(initials) > 0:
        return initials
    return str(driver_number)


def add_logo_marker(ax, x, y, driver_number, session=None, size=150):
    """
    Add a driver marker with logo circle at position (x, y)
    Uses driver number in colored circle (team color)
    """
    team_color = get_driver_team_color(driver_number)
    
    # Create driver identifier
    if session:
        identifier = get_driver_initials(session, driver_number)
    else:
        identifier = create_driver_marker_text(driver_number)
    
    # Create a circle with driver number/initials
    circle = Circle((x, y), radius=size*0.003, color=team_color, ec='white', 
                   linewidth=2, zorder=10, alpha=0.9)
    ax.add_patch(circle)
    
    # Add text on top
    ax.text(x, y, identifier, ha='center', va='center', 
           fontsize=8, fontweight='bold', color='white', zorder=11)


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
        
        ax.set_title(f'Fastest Lap Speed Map - {driver_label}\nLap Time: {lap_time}', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('X Position (m)')
        ax.set_ylabel('Y Position (m)')
        ax.set_aspect('equal')
        
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
        ax.set_xlabel('X Position (m)')
        ax.set_ylabel('Y Position (m)')
        ax.legend(fontsize=11)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
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
                        ax.set_aspect('equal')
                    else:
                        ax.text(0.5, 0.5, f"No telemetry data", 
                               ha='center', va='center', transform=ax.transAxes)
            
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


def plot_dynamic_track_animation(session, driver, driver_names_map=None, frame_skip=5):
    """
    Create an animated visualization of a driver's fastest lap.
    Shows the car moving around the track with live speed and position data.
    
    Args:
        session: FastF1 session object
        driver: Driver number to animate
        driver_names_map: Dictionary mapping driver numbers to driver names
        frame_skip: Number of telemetry points to skip for performance
    """
    if session is None:
        st.warning("No session data available")
        return
    
    try:
        # Get the fastest lap for the driver
        laps = session.laps.pick_drivers(driver)
        
        if len(laps) == 0:
            st.warning(f"No laps found for driver {driver}")
            return
        
        # Filter out laps with NaN lap times
        valid_laps = laps[laps['LapTime'].notna()]
        
        if len(valid_laps) == 0:
            st.warning(f"No valid laps found for driver {driver}")
            return
        
        fastest_lap = valid_laps.loc[valid_laps['LapTime'].idxmin()]
        
        # Get telemetry data
        try:
            telemetry = fastest_lap.get_telemetry()
        except:
            st.warning("Could not load telemetry for selected lap")
            return
        
        if telemetry is None or len(telemetry) == 0:
            st.warning("No telemetry data available")
            return
        
        # Subsample telemetry for animation smoothness
        telemetry_anim = telemetry.iloc[::frame_skip].reset_index(drop=True)
        
        if len(telemetry_anim) < 2:
            st.warning("Insufficient telemetry data for animation")
            return
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Calculate axis limits with padding
        x_min, x_max = telemetry['X'].min(), telemetry['X'].max()
        y_min, y_max = telemetry['Y'].min(), telemetry['Y'].max()
        x_margin = (x_max - x_min) * 0.1
        y_margin = (y_max - y_min) * 0.1
        
        ax.set_xlim(x_min - x_margin, x_max + x_margin)
        ax.set_ylim(y_min - y_margin, y_max + y_margin)
        ax.set_aspect('equal')
        
        # Plot the complete lap line
        ax.plot(telemetry['X'], telemetry['Y'], 'k--', alpha=0.3, linewidth=1, label='Lap Track')
        
        # Get team color for the driver
        team_color = get_driver_team_color(driver)
        driver_identifier = get_driver_initials(session, driver)
        
        # Initialize animated elements with team colors
        car, = ax.plot([], [], 'o', color=team_color, markersize=14, label='Car Position', zorder=5, 
                      markeredgecolor='white', markeredgewidth=2)
        car_label = ax.text([], [], '', fontsize=8, ha='center', va='center',
                           fontweight='bold', color='white', zorder=6)
        trajectory, = ax.plot([], [], '-', color=team_color, alpha=0.6, linewidth=2.5, label='Trajectory')
        speed_text = ax.text(0.02, 0.98, '', transform=ax.transAxes, 
                           fontsize=12, verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        lap_time_text = ax.text(0.02, 0.88, '', transform=ax.transAxes, 
                              fontsize=12, verticalalignment='top',
                              bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        progress_text = ax.text(0.02, 0.78, '', transform=ax.transAxes, 
                              fontsize=12, verticalalignment='top',
                              bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        driver_label = f"{driver} - {driver_names_map.get(str(driver), 'Unknown')}" if driver_names_map else str(driver)
        ax.set_title(f'Dynamic Track Animation - {driver_label}\nFastest Lap: {fastest_lap["LapTime"]}', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('X Position (m)', fontsize=11)
        ax.set_ylabel('Y Position (m)', fontsize=11)
        ax.grid(True, alpha=0.2)
        ax.legend(loc='lower right', fontsize=10)
        
        # Store trajectory for animation
        trajectory_x = []
        trajectory_y = []
        
        def animate(frame):
            """Animation update function"""
            if frame >= len(telemetry_anim):
                return car, car_label, trajectory, speed_text, lap_time_text, progress_text
            
            # Get current telemetry point
            current = telemetry_anim.iloc[frame]
            
            # Update car position
            car.set_data([current['X']], [current['Y']])
            
            # Update car label
            car_label.set_position((current['X'], current['Y']))
            car_label.set_text(driver_identifier)
            
            # Update trajectory
            trajectory_x.append(current['X'])
            trajectory_y.append(current['Y'])
            trajectory.set_data(trajectory_x, trajectory_y)
            
            # Update text displays
            speed = current['Speed']
            speed_text.set_text(f'Speed: {speed:.1f} km/h')
            
            # Calculate elapsed time
            elapsed_time = current['Time']
            speed_text.set_text(f'Speed: {speed:.1f} km/h')
            lap_time_text.set_text(f'Elapsed: {elapsed_time}')
            
            # Calculate progress percentage
            progress = (frame / len(telemetry_anim)) * 100
            progress_text.set_text(f'Progress: {progress:.1f}%')
            
            return car, car_label, trajectory, speed_text, lap_time_text, progress_text
        
        # Create animation
        anim = animation.FuncAnimation(fig, animate, frames=len(telemetry_anim),
                                      interval=50, blit=True, repeat=True)
        
        # Save animation as GIF to display in Streamlit
        try:
            with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            writer = PillowWriter(fps=20)
            anim.save(tmp_path, writer=writer)
            
            # Read the GIF file and display
            with open(tmp_path, 'rb') as f:
                gif_data = f.read()
            
            st.image(gif_data, caption=f'Animated Lap - {driver_label}')
            
            # Clean up temp file
            os.unlink(tmp_path)
        except Exception as e:
            # Fallback: display the figure without animation
            st.pyplot(fig)
            st.info(f"Animation export note: {str(e)}")
        
        plt.close(fig)
        
    except Exception as e:
        st.error(f"Error creating dynamic track animation: {str(e)}")


def plot_multi_driver_race_animation(session, drivers_list, driver_names_map=None, frame_skip=10):
    """
    Create an animated visualization comparing multiple drivers through the same lap.
    Shows all selected drivers moving around the track simultaneously.
    
    Args:
        session: FastF1 session object
        drivers_list: List of driver numbers to compare
        driver_names_map: Dictionary mapping driver numbers to driver names
        frame_skip: Number of telemetry points to skip for performance
    """
    if session is None:
        st.warning("No session data available")
        return
    
    if not drivers_list or len(drivers_list) == 0:
        st.warning("No drivers selected for animation")
        return
    
    try:
        # Get telemetry for all selected drivers
        driver_telemetries = {}
        colors = plt.cm.tab10(np.linspace(0, 1, len(drivers_list)))
        
        for driver, color in zip(drivers_list, colors):
            try:
                laps = session.laps.pick_drivers(driver)
                
                if len(laps) == 0:
                    continue
                
                # Filter out laps with NaN lap times
                valid_laps = laps[laps['LapTime'].notna()]
                
                if len(valid_laps) == 0:
                    continue
                
                fastest_lap = valid_laps.loc[valid_laps['LapTime'].idxmin()]
                
                telemetry = fastest_lap.get_telemetry()
                
                if telemetry is not None and len(telemetry) > 0:
                    driver_telemetries[driver] = {
                        'telemetry': telemetry.iloc[::frame_skip].reset_index(drop=True),
                        'color': color,
                        'lap_time': fastest_lap['LapTime']
                    }
            except Exception as driver_error:
                # Skip drivers with errors and continue
                continue
        
        if not driver_telemetries:
            st.warning("Could not load telemetry for any selected drivers")
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Calculate axis limits
        all_x = np.concatenate([data['telemetry']['X'].values for data in driver_telemetries.values()])
        all_y = np.concatenate([data['telemetry']['Y'].values for data in driver_telemetries.values()])
        
        x_min, x_max = all_x.min(), all_x.max()
        y_min, y_max = all_y.min(), all_y.max()
        x_margin = (x_max - x_min) * 0.1
        y_margin = (y_max - y_min) * 0.1
        
        ax.set_xlim(x_min - x_margin, x_max + x_margin)
        ax.set_ylim(y_min - y_margin, y_max + y_margin)
        ax.set_aspect('equal')
        
        # Plot track lines and initialize car objects
        car_objects = {}
        car_text_objects = {}
        trajectory_objects = {}
        trajectory_data = {}
        
        for driver, data in driver_telemetries.items():
            telemetry = data['telemetry']
            color = data['color']
            
            # Plot track
            ax.plot(telemetry['X'], telemetry['Y'], '--', color=color, alpha=0.2, linewidth=1)
            
            # Get team color for the driver
            team_color = get_driver_team_color(driver)
            
            # Create car marker with team color circle
            car, = ax.plot([], [], 'o', color=team_color, markersize=12, 
                          label=f"{driver}", zorder=5, markeredgecolor='white', markeredgewidth=1.5)
            car_objects[driver] = car
            
            # Create text label for driver number/initials  
            identifier = create_driver_marker_text(driver, get_driver_initials(session, driver))
            car_text, = ax.plot([], [], 'o', color=team_color, markersize=1, zorder=4)  # Invisible marker for text
            car_text_objects[driver] = {'marker': car_text, 'identifier': identifier}
            
            # Create trajectory line
            traj, = ax.plot([], [], '-', color=color, alpha=0.6, linewidth=2)
            trajectory_objects[driver] = traj
            trajectory_data[driver] = {'x': [], 'y': []}
        
        # Progress text
        progress_text = ax.text(0.02, 0.98, '', transform=ax.transAxes, 
                              fontsize=12, verticalalignment='top',
                              bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        ax.set_title('Multi-Driver Race Animation - Fastest Laps Comparison', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('X Position (m)', fontsize=11)
        ax.set_ylabel('Y Position (m)', fontsize=11)
        ax.grid(True, alpha=0.2)
        ax.legend(loc='lower right', fontsize=10, ncol=2)
        
        # Find max length for animation
        max_frames = max(len(data['telemetry']) for data in driver_telemetries.values())
        
        def animate(frame):
            """Animation update function for multiple drivers"""
            if frame >= max_frames:
                return list(car_objects.values()) + list(trajectory_objects.values()) + [progress_text]
            
            for driver, data in driver_telemetries.items():
                telemetry = data['telemetry']
                
                if frame < len(telemetry):
                    current = telemetry.iloc[frame]
                    car_objects[driver].set_data([current['X']], [current['Y']])
                    
                    # Update trajectory
                    trajectory_data[driver]['x'].append(current['X'])
                    trajectory_data[driver]['y'].append(current['Y'])
                    trajectory_objects[driver].set_data(
                        trajectory_data[driver]['x'],
                        trajectory_data[driver]['y']
                    )
            
            progress = (frame / max_frames) * 100
            progress_text.set_text(f'Progress: {progress:.1f}%')
            
            return list(car_objects.values()) + list(trajectory_objects.values()) + [progress_text]
        
        # Create animation
        anim = animation.FuncAnimation(fig, animate, frames=max_frames,
                                      interval=50, blit=True, repeat=True)
        
        # Save and display
        try:
            with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            writer = PillowWriter(fps=20)
            anim.save(tmp_path, writer=writer)
            
            # Read the GIF file and display
            with open(tmp_path, 'rb') as f:
                gif_data = f.read()
            
            st.image(gif_data, caption='Multi-Driver Race Animation')
            
            # Clean up temp file
            os.unlink(tmp_path)
        except Exception as e:
            st.pyplot(fig)
            st.info(f"Animation export note: {str(e)}")
        
        plt.close(fig)
        
    except Exception as e:
        st.error(f"Error creating multi-driver animation: {str(e)}")


def plot_race_progression_animation(session, driver_names_map=None, frame_skip=1):
    """
    Create an animated visualization of the entire race progression.
    Shows all drivers' positions throughout the entire race, lap by lap.
    
    Args:
        session: FastF1 session object
        driver_names_map: Dictionary mapping driver numbers to driver names
        frame_skip: Number of laps to skip for performance (1 = every lap)
    """
    if session is None or session.laps is None:
        st.warning("No session data available")
        return
    
    try:
        # Get all laps and drivers
        all_laps = session.laps.copy()
        drivers = session.drivers
        
        if len(drivers) == 0:
            st.warning("No driver data available")
            return
        
        # Get max lap number
        max_lap = int(all_laps['LapNumber'].max())
        
        if max_lap < 2:
            st.warning("Insufficient race data (less than 2 laps)")
            return
        
        # Prepare colors for drivers
        colors = plt.cm.tab20(np.linspace(0, 1, len(drivers)))
        driver_colors = {driver: colors[idx] for idx, driver in enumerate(drivers)}
        
        # Create figure with two subplots
        fig = plt.figure(figsize=(16, 10))
        ax_pos = fig.add_subplot(121)  # Position plot
        ax_time = fig.add_subplot(122)  # Lap time plot
        
        # Setup position plot
        ax_pos.set_xlim(0.5, len(drivers) + 0.5)
        ax_pos.set_ylim(len(drivers) + 1, 0)
        ax_pos.set_xlabel('Lap Number', fontsize=12)
        ax_pos.set_ylabel('Position', fontsize=12)
        ax_pos.set_title('Race Position Progression', fontsize=14, fontweight='bold')
        ax_pos.grid(True, alpha=0.3, axis='y')
        
        # Setup lap time plot
        ax_time.set_xlabel('Lap Number', fontsize=12)
        ax_time.set_ylabel('Lap Time (seconds)', fontsize=12)
        ax_time.set_title('Lap Times Throughout Race', fontsize=14, fontweight='bold')
        ax_time.grid(True, alpha=0.3)
        
        # Info text
        info_text = fig.text(0.5, 0.98, '', ha='center', fontsize=12,
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Store line objects for animation
        position_lines = {}
        laptime_lines = {}
        
        for driver in drivers:
            line, = ax_pos.plot([], [], 'o-', color=driver_colors[driver], 
                               markersize=8, linewidth=2, 
                               label=f"{driver} - {driver_names_map.get(str(driver), 'Unknown')}" if driver_names_map else str(driver))
            position_lines[driver] = line
            
            line2, = ax_time.plot([], [], 'o-', color=driver_colors[driver], 
                                 markersize=6, linewidth=2)
            laptime_lines[driver] = line2
        
        ax_pos.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=9, ncol=2)
        
        def animate(lap_num):
            """Animation update for each lap"""
            current_lap = lap_num * frame_skip
            
            if current_lap > max_lap:
                current_lap = max_lap
            
            # Get data up to current lap
            laps_to_display = all_laps[all_laps['LapNumber'] <= current_lap]
            
            # Update position plot
            for driver in drivers:
                driver_laps = laps_to_display[laps_to_display['Driver'] == driver]
                
                if len(driver_laps) > 0:
                    lap_nums = driver_laps['LapNumber'].values
                    positions = driver_laps['Position'].values
                    
                    # Filter out NaN positions
                    valid_idx = ~pd.isna(positions)
                    
                    if valid_idx.sum() > 0:
                        position_lines[driver].set_data(lap_nums[valid_idx], positions[valid_idx])
                    
                    # Update lap time plot
                    lap_times = pd.to_timedelta(driver_laps['LapTime']).dt.total_seconds()
                    lap_times = lap_times[~pd.isna(lap_times)]
                    
                    if len(lap_times) > 0:
                        laptime_lines[driver].set_data(
                            driver_laps[~pd.isna(driver_laps['LapTime'])]['LapNumber'].values,
                            lap_times.values
                        )
            
            # Auto-scale lap time plot
            all_times = []
            for driver in drivers:
                driver_laps = laps_to_display[laps_to_display['Driver'] == driver]
                lap_times = pd.to_timedelta(driver_laps['LapTime']).dt.total_seconds()
                lap_times = lap_times[~pd.isna(lap_times)]
                if len(lap_times) > 0:
                    all_times.extend(lap_times.values)
            
            if all_times:
                ax_time.set_ylim(min(all_times) * 0.95, max(all_times) * 1.05)
            
            # Update info
            current_leader = laps_to_display[laps_to_display['Position'] == 1.0]
            if len(current_leader) > 0:
                leader = current_leader.iloc[-1]['Driver']
                leader_label = f"{leader} - {driver_names_map.get(str(leader), 'Unknown')}" if driver_names_map else str(leader)
                info_text.set_text(f'Lap {int(current_lap)} / {int(max_lap)} | Leader: {leader_label}')
            else:
                info_text.set_text(f'Lap {int(current_lap)} / {int(max_lap)}')
            
            return list(position_lines.values()) + list(laptime_lines.values()) + [info_text]
        
        # Create animation
        total_frames = int(max_lap / frame_skip) + 1
        anim = animation.FuncAnimation(fig, animate, frames=total_frames,
                                      interval=100, blit=True, repeat=True)
        
        # Save and display
        try:
            with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            st.info("Creating race animation (this may take a minute)...")
            writer = PillowWriter(fps=10)
            anim.save(tmp_path, writer=writer)
            
            # Read and display
            with open(tmp_path, 'rb') as f:
                gif_data = f.read()
            
            st.image(gif_data, caption='Full Race Progression Animation')
            
            # Clean up
            os.unlink(tmp_path)
        except Exception as e:
            st.pyplot(fig)
            st.info(f"Animation export note: {str(e)}")
        
        plt.close(fig)
        
    except Exception as e:
        st.error(f"Error creating race progression animation: {str(e)}")


def plot_live_track_position_animation(session, driver_names_map=None, points_per_frame=5):
    """
    Create an animated visualization of the entire race on the actual track.
    Shows all drivers moving around the track circuit with live positions throughout the race.
    
    Args:
        session: FastF1 session object
        driver_names_map: Dictionary mapping driver numbers to driver names
        points_per_frame: Number of telemetry points to display per animation frame
    """
    if session is None or session.laps is None:
        st.warning("No session data available")
        return
    
    try:
        all_laps = session.laps.copy()
        drivers = session.drivers
        
        if len(drivers) == 0:
            st.warning("No driver data available")
            return
        
        # Prepare colors for drivers
        colors = plt.cm.tab20(np.linspace(0, 1, len(drivers)))
        driver_colors = {driver: colors[idx] for idx, driver in enumerate(drivers)}
        
        # Load telemetry data for all drivers across multiple laps
        driver_telemetries = {}
        drivers_attempted = 0
        drivers_failed = 0
        
        with st.spinner("Loading telemetry data from drivers..."):
            for driver in drivers:
                drivers_attempted += 1
                try:
                    laps = all_laps[all_laps['Driver'] == driver]
                    
                    if len(laps) == 0:
                        drivers_failed += 1
                        continue
                    
                    # Get valid laps with telemetry
                    valid_laps = laps[laps['LapTime'].notna()]
                    
                    if len(valid_laps) < 1:
                        drivers_failed += 1
                        continue
                    
                    # Try to collect telemetry for multiple laps
                    all_telemetry_points = []
                    lap_change_indices = []
                    
                    for idx, (_, lap) in enumerate(valid_laps.head(20).iterrows()):  # First 20 laps
                        try:
                            telemetry = lap.get_telemetry()
                            
                            if telemetry is not None and len(telemetry) > 0:
                                # Validate telemetry has required columns and data
                                if 'X' in telemetry.columns and 'Y' in telemetry.columns:
                                    # Check if coordinates are valid (not all NaN)
                                    if not (telemetry['X'].isna().all() or telemetry['Y'].isna().all()):
                                        # Add lap number information
                                        telemetry_with_lap = telemetry.copy()
                                        telemetry_with_lap['LapNum'] = int(lap['LapNumber'])
                                        all_telemetry_points.append(telemetry_with_lap)
                                        
                                        if len(all_telemetry_points) > 1:
                                            lap_change_indices.append(
                                                lap_change_indices[-1] + len(telemetry) if lap_change_indices else len(telemetry)
                                            )
                        except Exception as lap_error:
                            continue
                    
                    # If multi-lap telemetry collection failed or insufficient data, fallback to fastest lap
                    if not all_telemetry_points:
                        try:
                            # Fallback: Use only the fastest lap
                            fastest_lap = valid_laps.loc[valid_laps['LapTime'].idxmin()]
                            fallback_telemetry = fastest_lap.get_telemetry()
                            
                            if fallback_telemetry is not None and len(fallback_telemetry) > 0:
                                # Validate fallback telemetry
                                if 'X' in fallback_telemetry.columns and 'Y' in fallback_telemetry.columns:
                                    if not (fallback_telemetry['X'].isna().all() or fallback_telemetry['Y'].isna().all()):
                                        fallback_telemetry_with_lap = fallback_telemetry.copy()
                                        fallback_telemetry_with_lap['LapNum'] = int(fastest_lap['LapNumber'])
                                        all_telemetry_points = [fallback_telemetry_with_lap]
                        except Exception as fallback_error:
                            drivers_failed += 1
                            continue
                    
                    # Add to collection if we have any data
                    if all_telemetry_points:
                        combined_telemetry = pd.concat(all_telemetry_points, ignore_index=True)
                        # Final validation: ensure we have valid X,Y data
                        if not (combined_telemetry['X'].isna().all() or combined_telemetry['Y'].isna().all()):
                            driver_telemetries[driver] = {
                                'telemetry': combined_telemetry,
                                'color': driver_colors[driver],
                                'max_laps': len(all_telemetry_points)
                            }
                        else:
                            drivers_failed += 1
                    else:
                        drivers_failed += 1
                except Exception as driver_error:
                    drivers_failed += 1
                    continue
        
        if not driver_telemetries:
            st.error(f"Could not load telemetry data for animation. Attempted {drivers_attempted} drivers, but none had valid coordinate data.")
            st.info("This race may not have complete track geometry data. Try these alternatives:\n"
                   "1. Select a different race (2023-2026 have better data)\n"
                   "2. Use 'Single Driver Animation' instead (uses fastest lap)\n"
                   "3. Try 'Multi-Driver Animation' for comparison mode")
            return
        
        # Get track bounds
        try:
            all_x = np.concatenate([data['telemetry']['X'].dropna().values for data in driver_telemetries.values()])
            all_y = np.concatenate([data['telemetry']['Y'].dropna().values for data in driver_telemetries.values()])
            
            if len(all_x) == 0 or len(all_y) == 0:
                st.error("No valid track coordinate data available.")
                return
            
            x_min, x_max = all_x.min(), all_x.max()
            y_min, y_max = all_y.min(), all_y.max()
            x_margin = (x_max - x_min) * 0.15
            y_margin = (y_max - y_min) * 0.15
        except Exception as bounds_error:
            st.error(f"Error processing track coordinates: {str(bounds_error)}")
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(16, 12))
        
        ax.set_xlim(x_min - x_margin, x_max + x_margin)
        ax.set_ylim(y_min - y_margin, y_max + y_margin)
        ax.set_aspect('equal')
        ax.set_xlabel('X Position (m)', fontsize=12)
        ax.set_ylabel('Y Position (m)', fontsize=12)
        ax.set_title('Live Track Position Animation - Full Race', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.2)
        
        # Plot track outline for reference
        try:
            for driver, data in driver_telemetries.items():
                telemetry = data['telemetry']
                if 'X' in telemetry.columns and 'Y' in telemetry.columns:
                    # Get first lap track coordinates
                    first_lap_data = telemetry[telemetry['LapNum'] == telemetry['LapNum'].min()]
                    if len(first_lap_data) > 0:
                        x_coords = first_lap_data['X'].dropna().values
                        y_coords = first_lap_data['Y'].dropna().values
                        if len(x_coords) > 0 and len(y_coords) > 0:
                            ax.plot(x_coords, y_coords, color='gray', alpha=0.2, linewidth=1, zorder=1)
                            break  # Only need to draw track once
        except Exception as track_error:
            pass  # Skip track outline if there's an issue
        
        # Create car positions and labels
        car_markers = {}
        car_labels = {}
        driver_identifiers = {}
        trajectories = {}
        
        for driver, data in driver_telemetries.items():
            # Get team color for better visibility
            team_color = get_driver_team_color(driver)
            
            # Create marker with team color and white edge
            marker, = ax.plot([], [], 'o', color=team_color, markersize=14, 
                            label=f"{driver} - {driver_names_map.get(str(driver), 'Unknown')}" if driver_names_map else str(driver),
                            zorder=5, markeredgecolor='white', markeredgewidth=2)
            car_markers[driver] = marker
            
            # Get driver identifier (initials or number)
            identifier = get_driver_initials(session, driver) if session else str(driver)
            driver_identifiers[driver] = identifier
            
            # Create label text for driver identifier
            label = ax.text(0, 0, '', fontsize=10, ha='center', va='center',
                          fontweight='bold', color='white', zorder=6)
            car_labels[driver] = label
            
            traj, = ax.plot([], [], color=team_color, alpha=0.4, linewidth=1.5, zorder=2)
            trajectories[driver] = {'line': traj, 'x': [], 'y': []}
        
        # Info text
        info_text = ax.text(0.02, 0.98, '', transform=ax.transAxes, fontsize=12,
                          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                          verticalalignment='top')
        
        ax.legend(loc='upper right', fontsize=10, ncol=2)
        
        # Find max points
        max_points = max(len(data['telemetry']) for data in driver_telemetries.values())
        
        def animate(frame_idx):
            """Animation update for race track visualization"""
            point_idx = frame_idx * points_per_frame
            
            if point_idx >= max_points:
                point_idx = max_points - 1
            
            for driver, data in driver_telemetries.items():
                telemetry = data['telemetry']
                
                if point_idx < len(telemetry):
                    current = telemetry.iloc[point_idx]
                    
                    # Skip if coordinates are NaN
                    if pd.isna(current['X']) or pd.isna(current['Y']):
                        continue
                    
                    # Update car position
                    car_markers[driver].set_data([current['X']], [current['Y']])
                    
                    # Update driver identifier label
                    lap_num = int(current.get('LapNum', 1))
                    identifier = driver_identifiers[driver]
                    car_labels[driver].set_position((current['X'], current['Y']))
                    car_labels[driver].set_text(f"{identifier}")
                    
                    # Update trajectory (keep last 50 points)
                    trajectories[driver]['x'].append(current['X'])
                    trajectories[driver]['y'].append(current['Y'])
                    
                    if len(trajectories[driver]['x']) > 50:
                        trajectories[driver]['x'].pop(0)
                        trajectories[driver]['y'].pop(0)
                    
                    trajectories[driver]['line'].set_data(
                        trajectories[driver]['x'],
                        trajectories[driver]['y']
                    )
            
            # Update info
            if point_idx < max_points:
                progress = (point_idx / max_points) * 100
                info_text.set_text(f'Race Progress: {progress:.1f}%\nPosition: {point_idx}/{max_points}')
            
            return list(car_markers.values()) + list(car_labels.values()) + \
                   [traj['line'] for traj in trajectories.values()] + [info_text]
        
        # Create animation
        total_frames = int(max_points / points_per_frame) + 1
        anim = animation.FuncAnimation(fig, animate, frames=total_frames,
                                      interval=50, blit=True, repeat=True)
        
        # Save and display
        try:
            with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            st.info("Creating track animation (this may take 2-3 minutes)...")
            writer = PillowWriter(fps=15)
            anim.save(tmp_path, writer=writer)
            
            # Read and display
            with open(tmp_path, 'rb') as f:
                gif_data = f.read()
            
            st.image(gif_data, caption='Full Race Track Animation - All Drivers')
            
            # Clean up
            os.unlink(tmp_path)
        except Exception as e:
            st.pyplot(fig)
            st.info(f"Animation export note: {str(e)}")
        
        plt.close(fig)
        
    except Exception as e:
        st.error(f"Error creating live track animation: {str(e)}")
