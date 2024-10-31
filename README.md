# Reddit Lead Manager

<img src="https://github.com/user-attachments/assets/a496b05a-386f-4a07-a3a6-00f0dc9a2908" style="width: 300px;" align="right" />This is an interactive lead management and analytics tool for tracking and analyzing leads collected from various online sources, such as Reddit. Built with Python and Streamlit, Reddit Lead Manager provides data visualization, filtering, and export capabilities, making it ideal for sales and marketing teams who wish to better understand their lead funnel and activity.

**Table of Contents**
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Lead Management**: Import, filter, and manage leads with ease. Supports CSV file upload to sync leads and save them locally.
- **Data Analytics**: Provides insights into lead distribution, conversion rates, daily activity, and more with intuitive visualizations.
- **Status Tracking**: Track each lead's progression through the sales funnel.
- **Interactive Interface**: Built with Streamlit, allowing for real-time filtering, bulk updates, and note-taking.
- **Export Options**: Export analytics summaries, status reports, and detailed lead data in CSV and JSON formats.

![Screenshot 2024-10-31 at 6 27 03 AM (4)](https://github.com/user-attachments/assets/f549d762-27a4-4170-8875-00fba69099f5)

![Screenshot 2024-10-31 at 6 27 14 AM (4)](https://github.com/user-attachments/assets/d3f14df9-e5d7-4b35-9dbb-9d990397fc95)

![Screenshot 2024-10-31 at 6 27 40 AM (4)](https://github.com/user-attachments/assets/3467fd3e-caba-440d-9a40-fb9487c61a1a)

## Project Structure

- **`analytics.py`**: Defines `AnalyticsManager`, which performs data analysis on leads, generating insights like status distribution and conversion rates.
- **`lead_manager.py`**: Contains `LeadManager`, responsible for loading, syncing, and updating lead data.
- **`main.py`**: Main Streamlit interface for interacting with lead data, applying filters, and updating statuses.
- **`pages/analytics.py`**: Adds an analytics page in the Streamlit app, showcasing data visualizations and metrics.
- **`storage.py`**: Implements `LocalStorage`, a utility for saving and loading lead data from a local file.
- **`utils.py`**: Contains helper functions for text cleaning and date formatting.

## Installation

To set up the Reddit Lead Manager application locally, follow these steps:

### Prerequisites

- Python 3.8 or higher
- [Pip](https://pip.pypa.io/en/stable/)

### Setup

1. **Clone the repository**:
    ```bash
    git clone https://github.com/marc-shade/Reddit-Lead-Manager.git
    cd Reddit-Lead-Manager
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Initialize local storage**:
    Ensure a `data` directory exists in the project root with a `progress.csv` file. This file will store your lead data. The `LocalStorage` class in `storage.py` will manage loading and saving this file.

## Usage

1. **Run the application**:
    ```bash
    streamlit run main.py
    ```

2. **Uploading Leads**:
   - From the application interface, use the "Upload your own CSV file" option to upload a CSV containing leads.
   - The file should have the columns: `summary`, `lowHangingFruit`, `originalPost`, `solution`, `date`, `url`, `subreddit`.

3. **Lead Filters and Updates**:
   - Apply filters based on lead status and subreddit to view relevant leads.
   - Select leads for bulk status updates or to add bulk notes.
   - For individual leads, edit the status or add notes directly in the interface.

4. **Export Options**:
   - Use the sidebar options on the analytics page to export a status report (CSV), detailed lead data (CSV), or a complete analytics summary (JSON).

## Configuration

Reddit Lead Manager includes a `pyproject.toml` file to configure package requirements and dependencies. Update this file as needed if adding or upgrading dependencies.

