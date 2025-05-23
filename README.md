# 🎧 Spotify Wrapped Dashboard

![Spotify Logo](https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg)

An interactive and visually polished Streamlit dashboard that turns your Spotify listening data into an immersive analytics experience — inspired by Spotify Wrapped.

## 📽 Demo Video

<!-- Replace the URL below with your uploaded video link on GitHub -->
Go to:
Videos and Screenshots/Spotify Analytics Project.mp4

---

## ✨ Features

- 🎵 **Top Tracks & Artists** with embedded Spotify previews  
- 📅 **Year-wise Filtering** via interactive checkboxes  
- 📈 **Listening Trends** by day, time of day, and month  
- 🗺️ **Geographic Listening Patterns** across countries  
- 🔀 **Shuffle vs. Non-Shuffle**, **Offline vs. Online**  
- 🏆 **Longest Listening Streaks & Milestones**  
- 📊 **Platform Comparison**: Android, iOS, Web, etc.  
- 🎤 **Artist-Specific Analysis** (with Wikipedia image integration)  
- 🎨 **Custom Dark UI Theme** styled with CSS and hover animations  

---

## 📂 Project Structure

```bash
spotify-wrapped-dashboard/
├── spotify_dashboard_spotify_theme.py   # Main Streamlit dashboard code
├── df_clean.csv                         # Your cleaned Spotify listening data
├── README.md                            # This documentation
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/spotify-wrapped-dashboard.git
cd spotify-wrapped-dashboard
```

### 2. Install dependencies

```bash
pip install streamlit pandas plotly requests
```

### 3. Prepare your data

Rename your Spotify listening history CSV to:

```bash
df_clean.csv
```

Ensure the dataset includes these key fields:
- `ts_local_clean` (timestamp)
- `ms_played`
- `master_metadata_track_name`
- `master_metadata_album_artist_name`
- `platform_clean`
- `conn_country_full`

### 4. Launch the dashboard

```bash
streamlit run spotify_dashboard_spotify_theme.py
```

---

## 🖼 Sample Preview

<!-- Replace this image URL with a screenshot of your dashboard -->
![Dashboard Preview](https://github.com/YashChaudhary16/Spotify/blob/main/Videos%20and%20Screenshots/Screenshot%202025-05-22%20191005.png)

---

## 🛠 Customization Ideas

- Export report as PDF or PNG    
- A CI/CD pipeline to pre-process data (from json) as required by this project.
- Add song recommendations based on patterns  

---

## 📃 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- [Spotify](https://www.spotify.com) – inspiration and data  
- [Streamlit](https://streamlit.io/) – dashboarding framework  
- [Plotly](https://plotly.com/) – interactive visualizations  

---

## 🤝 Contribute

Want to enhance the dashboard, fix bugs, or request features?  
Feel free to open an issue or submit a pull request!
