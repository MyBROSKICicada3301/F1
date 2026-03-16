"""Helper functions for Formula 1 data processing and formatting."""
import fastf1
import pandas as pd
from datetime import datetime


def get_seasons():
    """
    Get list of available Formula 1 seasons with complete race data.
    
    FastF1 has comprehensive data for 2019 onwards.
    Earlier years are excluded to ensure data completeness.
    """
    # Complete datasets available from 2019 through 2025
    return list(range(2019, 2026))


def get_events(year):
    """
    Retrieve all Grand Prix events for a specific season.
    
    Filters out non-race events and returns event names in competition order.
    """
    try:
        schedule = fastf1.get_event_schedule(year)
        # Filter only events with race dates, exclude test/non-race events
        events = schedule[schedule['EventDate'].notna()]['EventName'].tolist()
        return events
    except Exception as e:
        print(f"Error fetching events for {year}: {e}")
        return []


def format_time(seconds):
    """
    Convert seconds into a readable time format: MM:SS.mmm
    Example: 92.433 becomes "1:32.433"
    Handles missing or NaN values gracefully.
    """
    if pd.isna(seconds):
        return "N/A"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}:{secs:06.3f}"


def format_time_detailed(seconds):
    """
    Convert seconds into detailed human-readable format.
    Example: 92.433 seconds becomes "1 minute 32 seconds 433 milliseconds"
    """
    if pd.isna(seconds):
        return "N/A"
    
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    whole_seconds = int(remaining_seconds)
    milliseconds = int((remaining_seconds - whole_seconds) * 1000)
    
    minute_text = f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"
    second_text = f"{whole_seconds} second" if whole_seconds == 1 else f"{whole_seconds} seconds"
    
    return f"{minute_text} {second_text} {milliseconds} milliseconds"


def get_driver_name(driver_code):
    """Retrieve the full driver name from a three-letter driver code."""
    try:
        driver = fastf1.get_driver(driver_code)
        return f"{driver['FirstName']} {driver['LastName']}"
    except:
        return driver_code
