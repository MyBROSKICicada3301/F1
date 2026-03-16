# F1 Interactive Dashboard
{STILL IN PROGRESS}

A web-based dashboard for exploring F1 race data, telemetry, and driver comparisons using **FastF1** and **Streamlit**.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run main.py
```

Open `http://localhost:8501` in your browser.

## Features

- **Race Results** - Podium finishers and race statistics
- **Driver Analysis** - Lap times, sector performance, tire degradation
- **Driver Comparison** - Head-to-head lap time analysis
- **Lap Telemetry** - Speed, throttle, and distance data visualization
- **Race Visualizer** - Position changes, track maps, and speed heatmaps
- **Tire Strategy** - Compound analysis and pit stop patterns

## Project Structure

```
├── main.py              # Streamlit app with 6-page navigation
├── data_loader.py       # FastF1 data fetching and caching
├── visualization.py     # Performance analysis plots
├── race_visualizer.py   # Track-based race visualizations
├── utils.py            # Helpers (time formatting, season/event data)
└── requirements.txt     # Dependencies
```

## Tech Stack

Python 3.14 | FastF1 | Streamlit | Pandas | Matplotlib

## To-Do

- [ ] Fix ValueError: cannot convert float NaN to integer (telemetry parsing)
- [ ] Debug race visualizer track rendering issues
- [ ] Replace deprecated Streamlit `use_container_width` parameter
- [ ] Add corner annotations to track maps
- [ ] Optimize performance for large datasets
- **Weather Analysis** - Correlate weather data with performance
- **Monte Carlo Simulations** - Predict championship scenarios
- **Interactive Track Maps** - Fan-animated corner speed visualization
- **Export Reports** - Generate PDF pit wall reports

## Troubleshooting

### Session won't load
- Check internet connection (FastF1 fetches live data)
- Verify the season and event are valid
- Wait a moment and refresh the page

### Slow performance
- First load is slower; subsequent views are cached
- FastF1 cache is stored in `f1_cache/` directory
- Clearing cache: delete the `f1_cache/` folder

### Missing driver data
- Some drivers may have incomplete data for certain sessions
- Practice sessions have fewer drivers than races
- Qualifying sessions may have different participants

## References

- **FastF1 Documentation**: https://docs.fastf1.dev/
- **Streamlit Docs**: https://docs.streamlit.io/
- **F1 Data Guide**: https://f1-api.readthedocs.io/

## License

This project is for educational purposes and uses publicly available F1 data through FastF1.

---

**Happy analyzing! ☮️**
