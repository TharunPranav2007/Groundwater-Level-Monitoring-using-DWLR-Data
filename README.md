# 💧 Groundwater Level Monitoring & Evaluation Dashboard

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red.svg)](https://streamlit.io)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-yellow.svg)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-5.15%2B-green.svg)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)

An interactive web application built with Streamlit for the real-time visualization, analysis, and evaluation of groundwater resources using Digital Water Level Recorder (DWLR) data.

---

## 🚀 Live Demo

You can access the deployed application here:

**[https://groundwater-level-monitoring-using-dwlr-data-design-studio.streamlit.app/](https://groundwater-level-monitoring-using-dwlr-data-design-studio.streamlit.app/)**

---

## ✨ Features

* **🌐 Interactive Dashboard:** A clean, modern, and user-friendly interface for data exploration.
* **📍 Dynamic Location Filtering:** Easily filter groundwater data by State, District, Block, Village, Pincode, or even a manual text search.
* **📊 Key Performance Indicators (KPIs):** At-a-glance cards showing Overall, Current, Premonsoon, and Postmonsoon average Depth to Water Level (DTWL).
* **📈 Historical Trend Analysis:** Visualize yearly trends for Premonsoon, Postmonsoon, and Overall groundwater levels using interactive Plotly line charts.
* **🗺️ Geospatial Mapping:** An interactive map from Plotly shows the latest recorded DTWL at various monitoring stations.
* **🌦️ Real-time Weather Integration:** Fetches and displays current temperature and humidity for the selected location using the OpenWeatherMap API.
* **🌱 Rule-Based Crop Recommendation:** Provides intelligent crop suggestions based on the region, average water level, and current temperature.
* **📂 Data Export:** Download a comprehensive report in CSV format, including a summary of metrics and the filtered raw data.



---

## 🛠️ Tech Stack

* **Backend:** Python
* **Web Framework:** Streamlit
* **Data Manipulation:** Pandas, NumPy
* **Data Visualization:** Plotly Express
* **API Integration:** Requests (for OpenWeatherMap)

---

## 💾 Data Source

The historical groundwater level data is included directly in this repository. The Streamlit application is coded to load these files from the GitHub repository itself, ensuring that the deployed app and local versions run seamlessly without needing local data management.

The dataset is partitioned into the following files:
* `august_wl_1994-2023_compressed-clean.csv`
* `january_wl_1994-2024-compressed-clean.xlsx`
* `post-monsoon_wl_1994-2023_compressed-clean.xlsx`
* `pre-monsoon_1994-2003-clean.csv`
* `pre-monsoon_2004-2013-clean.csv`
* `pre-monsoon_2014-2024-clean.csv`

---

## ⚙️ Local Setup and Installation

To fork this repository and run the application on your local machine, follow these steps.

### 1. Fork the Repository

First, create a copy of this repository in your own GitHub account.
* Click the **Fork** button at the top-right corner of this page.

### 2. Clone Your Forked Repository

Next, clone the forked repository to your local machine. Replace `<YOUR_USERNAME>` with your GitHub username.

```bash
git clone [https://github.com/](https://github.com/)<YOUR_USERNAME>/Groundwater-Level-Monitoring-using-DWLR-Data.git
cd Groundwater-Level-Monitoring-using-DWLR-Data
```

### 3. Create a Virtual Environment

It's a best practice to create a virtual environment to manage project-specific dependencies.

```bash
# For Windows
python -m venv venv
.\venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

Install all the required packages using the `requirements.txt` file included in the repository.

```bash
pip install -r requirements.txt
```

### 5. Set Up API Keys (Important!)

The application uses the **OpenWeatherMap API** to fetch weather data. You should use Streamlit's secrets management instead of hardcoding the API key.

1.  **Get an API Key:** Sign up on [OpenWeatherMap](https://home.openweathermap.org/users/sign_up) and get your free API key.

2.  **Create a Secrets File:**
    * In your project directory, create a new folder named `.streamlit`.
    * Inside the `.streamlit` folder, create a file named `secrets.toml`.

3.  **Add Your Key to `secrets.toml`:**
    ```toml
    # .streamlit/secrets.toml
    OPENWEATHER_API_KEY = "your_actual_api_key_here"
    ```

4.  **Update the Python Script:**
    Modify the `DWLR_App.py` script to use the secret. Find this line:
    ```python
    OPENWEATHER_API_KEY = "223b9d01eaaae4062b28a2579793e770"
    ```
    And **replace** it with this line to securely access your key:
    ```python
    OPENWEATHER_API_KEY = st.secrets["OPENWEATHER_API_KEY"]
    ```

### 6. Run the Application

Now you are ready to run the Streamlit app!

```bash
streamlit run DWLR_App.py
```

The application should now be running and accessible in your web browser at `http://localhost:8501`.

---

## 📂 Project Structure

```
.
├── DWLR_App.py                                     # Main Streamlit application script
├── README.md                                       # Project documentation
├── requirements.txt                                # List of Python dependencies
├── august_wl_1994-2023_compressed-clean.csv        # Data file for August
├── january_wl_1994-2024-compressed-clean.xlsx      # Data file for January
├── post-monsoon_wl_1994-2023_compressed-clean.xlsx # Data file for Post-Monsoon
├── pre-monsoon_1994-2003-clean.csv                 # Data file for Pre-Monsoon (1994-2003)
├── pre-monsoon_2004-2013-clean.csv                 # Data file for Pre-Monsoon (2004-2013)
└── pre-monsoon_2014-2024-clean.csv                 # Data file for Pre-Monsoon (2014-2024)
```

---

## 🤝 How to Contribute

Contributions are welcome! If you'd like to improve the dashboard or add new features, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/AmazingNewFeature`).
3.  Make your changes and commit them (`git commit -m 'Add some AmazingNewFeature'`).
4.  Push to the branch (`git push origin feature/AmazingNewFeature`).
5.  Open a **Pull Request**.

---

## 📜 License

This project is licensed under the MIT License.

---

## ✍️ Authors

* **Tharun Pranav T** - [LinkedIn Profile](https://www.linkedin.com/in/tharun-pranav-t-274a18327?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)
