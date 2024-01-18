# Streamlit Golf
Visual component to garmin golf data project that relies on the database output from: [Garmin Golf Processor](https://github.com/benwittbrodt/golf_stats)

The structure is within the app folder: 

* ui.py - Anything related to the actual output in streamlit, imports functions from the graphs file
* graphs.py - Calls functions for the datasets and processes anything into a graph from plotly
* data.py - Main interface with the database connecting to it and querying to set up dataframes for the graphs

Requires a config.toml file for the database location within the same file system 

For example: `db_src = 'golf.db'` will find the database within the same root folder as the cloned project

 
