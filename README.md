# F1 Interactive Dashboard

A web-based dashboard for exploring F1 race data, telemetry, and driver comparisons using FastF1 and Streamlit.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run main.py
```

Open `http://localhost:8501` in your browser(currently testing locally).

## Features

### Core Analytics
- **Race Results** - Podium finishers and race statistics
- **Driver Analysis** - Lap times, sector performance, tire degradation
- **Driver Comparison** - Head-to-head lap time analysis
- **Lap Telemetry** - Speed, throttle, and distance data visualization
- **Tire Strategy** - Compound analysis and pit stop patterns

### Track Visualizations
- **Position Changes Over Race** - Dynamic position progression with live graphs
- **Fastest Lap Analysis** - Speed maps showing corner speeds
- **Driver Lap Comparison** - Compare two drivers' best laps on the same track
- **Speed Distribution Heatmaps** - Identify fast and slow sections for top drivers
- **Lap Time Consistency** - Box plots showing driver consistency analysis

### Race Animations
- **Single Driver Animation** - Watch a driver's fastest lap with live telemetry data
- **Multi-Driver Animation** - Compare multiple drivers' fastest laps simultaneously
- **Live Track Position Animation** - Watch the entire race unfold on the actual track circuit with all drivers racing in real-time (to be fixed)

## Project Structure

```
├── main.py              # Streamlit app with 6-page navigation
├── data_loader.py       # FastF1 data fetching and caching
├── visualization.py     # Performance analysis plots
├── race_visualizer.py   # Dynamic track visualizations and race animations
├── utils.py            # Helpers (time formatting, season/event data)
└── requirements.txt     # Dependencies
```

## Tech Stack

- Python 3.10+ 
- FastF1 3.0+ 
- Streamlit 
- Pandas 
- Matplotlib 
- Pillow

## Recent Updates

- **Fixed deprecated FastF1 API calls** - Replaced `pick_driver` with `pick_drivers`  
- **Added dynamic race animations** - GIF-based animations showing lap-by-lap progression  
- **Fixed track visualization errors** - Removed deprecated `plot_track` function calls  
- **Improved telemetry handling** - Better NaN value filtering for robustness  
- **Added multi-driver race animation** - Simultaneous visualization of multiple drivers  

## To-Do

### Bug Fixes
- [ ] Fix Live Track Position Animation - "Could not load telemetry data for animation" error
  - Issue: Some races/drivers missing telemetry data across multiple laps
  - Solution: Add fallback to single lap telemetry or interpolate data(need to see which is best)

### New Features
- [ ] Add team logos for driver representation (Ferrari, Mercedes, Red Bull, etc.)
- [ ] Improve UI with gradient backgrounds and modern color schemes
- [ ] Add championship standings prediction using Monte Carlo
- [ ] Add real-time standings widget during race
- [ ] Implement dark mode/accessibility toggle

## Installation Details

### Requirements
- Python 3.10 or higher
- FastF1 >= 3.0.0
- Virtual environment (recommended if python interpreter version unavailable)

### Troubleshooting

**Session won't load**
- Check internet connection (FastF1 fetches live data)
- Verify the season and event are valid
- Wait a moment and refresh the page

**Slow performance**
- First load is slower; subsequent views are cached
- FastF1 cache is stored in `f1_cache/` directory
- Clearing cache: delete the `f1_cache/` folder

**Animation takes too long**
- Reduce the animation resolution or skip more frames
- Use a faster computer for better GIF encoding
- Animations are normal for first run; cached on subsequent loads

**Live Track Position Animation shows "Could not load telemetry data"**
- This occurs when a race/driver has incomplete telemetry across laps
- Try selecting a different race or driver
- Works best with recent races (2023-2026) that have complete data
- Workaround: Use "Single Driver Animation" instead
- Fix to be added soon: Will add fallback to single lap or interpolated data

**Missing driver data**
- Some drivers may have incomplete data for certain sessions
- Practice sessions have fewer drivers than races
- Qualifying sessions may have different participants

## References

- **FastF1 Documentation**: https://docs.fastf1.dev/
- **Streamlit Docs**: https://docs.streamlit.io/
- **F1 Official Data**: https://www.formula1.com/
- **Dynamic Track Animation Guide**:https://python.plainenglish.io/creating-a-dynamic-track-animation-from-an-f1-lap-time-simulator-fb2ba7e93317

## License

This project is for educational purposes and uses publicly available F1 data through FastF1.

---

**Version: 2.0** | Last Updated: March 2026  