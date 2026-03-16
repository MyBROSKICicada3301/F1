"""Load and process Formula 1 data from FastF1 with efficient caching."""
import fastf1
import pandas as pd
import streamlit as st
from functools import lru_cache

# Enable FastF1 local cache for faster subsequent data retrievals
fastf1.Cache.enable_cache('f1_cache')


@st.cache_data(ttl=3600)
def load_session(year, event_name, session_type='R'):
    """
    Load a Formula 1 session with telemetry and weather data.
    
    Parameters
    ----------
    year : int
        Championship year
    event_name : str
        Name of the Grand Prix event
    session_type : str
        Type of session (R for Race, Q for Qualifying, FP1/FP2/FP3 for Practice)
    
    Returns
    -------
    session : fastf1.Session or None
        Loaded session object with telemetry data
    """
    try:
        session = fastf1.get_session(year, event_name, session_type)
        session.load(telemetry=True, weather=True)
        return session
    except Exception as e:
        st.error(f"Error loading session: {e}")
        return None


@st.cache_data(ttl=3600)
def get_race_results(year, event_name):
    """Get final race results."""
    try:
        session = load_session(year, event_name, 'R')
        if session is None:
            return None
        results = session.results[['Abbreviation', 'FullName', 'Position', 'Points']]
        results = results.dropna(subset=['Position'])
        results = results.sort_values('Position')
        return results.head(20)
    except Exception as e:
        st.error(f"Error fetching results: {e}")
        return None


@st.cache_data(ttl=3600)
def get_driver_laps(year, event_name, driver_abbr):
    """Get all laps for a specific driver."""
    try:
        session = load_session(year, event_name, 'R')
        if session is None:
            return None
        laps = session.laps.pick_driver(driver_abbr)
        return laps
    except Exception as e:
        st.error(f"Error loading driver laps: {e}")
        return None


@st.cache_data(ttl=3600)
def get_driver_names_map(year, event_name):
    """Get mapping of driver numbers to names."""
    try:
        session = load_session(year, event_name, 'R')
        if session is None:
            return {}
        
        # Build driver name map from results
        driver_map = {}
        if hasattr(session, 'results') and session.results is not None:
            for idx, row in session.results.iterrows():
                driver_num = str(row['DriverNumber']) if 'DriverNumber' in row.index else str(idx)
                driver_name = row['FullName'] if 'FullName' in row.index else "Unknown"
                driver_map[str(int(float(driver_num)))] = driver_name
        
        return driver_map
    except Exception as e:
        return {}


def format_driver_name(driver_number, driver_map):
    """Format driver display name with number."""
    driver_name = driver_map.get(str(driver_number), "Unknown Driver")
    return f"{driver_number} - {driver_name}"


@st.cache_data(ttl=3600)
def get_driver_comparison(year, event_name, driver1, driver2):
    """Compare two drivers' performance."""
    try:
        session = load_session(year, event_name, 'R')
        if session is None:
            return None, None
        
        laps1 = session.laps.pick_driver(driver1)
        laps2 = session.laps.pick_driver(driver2)
        
        return laps1, laps2
    except Exception as e:
        st.error(f"Error in driver comparison: {e}")
        return None, None


@st.cache_data(ttl=3600)
def get_lap_telemetry(year, event_name, driver_abbr, lap_number):
    """Get telemetry for a specific lap."""
    try:
        session = load_session(year, event_name, 'R')
        if session is None:
            return None
        
        laps = session.laps.pick_driver(driver_abbr)
        if lap_number > len(laps) or lap_number < 1:
            return None
        
        lap = laps.iloc[lap_number - 1]
        telemetry = lap.get_telemetry()
        return telemetry
    except Exception as e:
        st.error(f"Error loading telemetry: {e}")
        return None


@st.cache_data(ttl=3600)
def get_track_status(year, event_name):
    """Get track status during the race."""
    try:
        session = load_session(year, event_name, 'R')
        if session is None:
            return None
        return session.track_status_data
    except Exception as e:
        st.error(f"Error loading track status: {e}")
        return None
