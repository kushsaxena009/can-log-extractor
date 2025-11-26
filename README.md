# CAN Log Extractor + Visualizer

A beginner-friendly Python tool for extracting, cleaning, and visualizing CAN network logs.

## Features
- Load ASC / CSV CAN logs
- Basic summary metrics
- Data ready for visualization

## Requirements
- python-can
- pandas
- matplotlib

## How to Run

## How to Use

### Load a log
from extractor import CANLogExtractor
log = CANLogExtractor("yourfile.asc")
log.load_log()

### Basic summary
log.get_summary()

### Filter examples
log.filter_by_id("0x100")
log.filter_by_time(0.0, 1.0)

### Visualization
log.plot_id_frequency()
