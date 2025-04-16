# Data Directory

This directory contains the data files used by the AI-GAPSIM application. The data is organized into the following structure:

```
data/
├── WECC data/           # Current WECC power grid data
│   ├── merged_branch_data.xlsx    # Transmission lines
│   ├── merged_gen_data.xlsx       # Generators
│   ├── merged_bus_data.xlsx       # Buses
│   ├── merged_substation_data.xlsx # Substations
│   └── merged_load_data.xlsx      # Loads
├── WECC 2032 data/      # Future projections for 2032
├── EEA-CIPV.xlsx        # Energy Emergency Alert data for CIPV
├── EEA-AESO.xlsx        # Energy Emergency Alert data for AESO
├── BA_GPS_Data.xlsx     # Balancing Authority GPS coordinates
└── 24Bus_Data.xlsx      # 24-bus system model
```

## Data Sources

The data in this directory comes from the following sources:

1. **WECC Power Grid Data**: Western Electricity Coordinating Council (WECC) power grid system data, including transmission lines, generators, loads, substations, and buses.

2. **Balancing Authority Data**: Information about Balancing Authorities (BAs) in the WECC region, including their boundaries and Energy Emergency Alert (EEA) events.

3. **Weather Data**: The application fetches weather data from external sources or generates synthetic data for demonstration purposes.

## Data Format

Most data files are in Excel (.xlsx) format with the following structure:

- **Grid Component Data**: Contains component information and geometry data in WKT (Well-Known Text) format for geospatial representation.
- **Balancing Authority Data**: Contains BA boundaries as polygons in WKT format and associated metadata.
- **EEA Data**: Contains Energy Emergency Alert events with dates, levels, and descriptions.

## Adding Your Own Data

To use your own data with the application:

1. Ensure your data follows the same structure as the existing files.
2. Place your files in the appropriate subdirectory.
3. Update the database with your new data using the data import scripts.

## Note

The actual data files are not included in the repository due to size constraints and licensing considerations. You will need to obtain the data from the appropriate sources and place them in this directory.
