# Folders Synchronization Tool

## Overview

The Folders Synchronization Tool is a Python application designed to keep two directories synchronized at all times. This tool continuously monitors a source folder and ensures that a replica folder mirrors its contents, making it ideal for backup and data consistency.

## Features

- **Real-time Synchronization**: Automatically updates the replica folder to match the source folder.
- **Command-Line Interface**: Easily configurable through command-line arguments.
- **Logging**: Comprehensive logging of all activities, including synchronization events and error handling.
- **Robust Error Handling**: Gracefully manages exceptions to ensure uninterrupted operation.
- **Manual Termination**: The program runs indefinitely until manually stopped.

## Requirements

- Python 3 or higher

## Installation

Clone the repository:
   
   **git clone https://github.com/yourusername/folders-synchronization-tool.git**
   
## How to Use

1. Open your terminal or command prompt.
2. Run the tool using the following command format:

**python folders_sync_v1.py <source_folder> <replica_folder> <interval_time_in_seconds> <log_file_path>**

<source_folder>: The path to the directory you want to monitor.
<replica_folder>: The path to the directory that will be updated.
<interval_time_in_seconds>: The interval between synchronization cycles (in seconds).
<log_file_path>: The path to the log file for recording execution data.
