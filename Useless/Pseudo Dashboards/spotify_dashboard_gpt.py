
import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("df_clean.csv", parse_dates=["ts_local_clean"])
    return df

df = load_data()

# Preprocessing
df['hours'] = df['ms_played'] / (1000 * 60 * 60)
df['minutes'] = df['ms_played'] / (1000 * 60)
df['date'] = pd.to_datetime(df['ts_local_clean']).dt.date


# Sidebar
st.sidebar.title("Spotify Wrapped Dashboard")
top_n = st.sidebar.slider("Top N Tracks", min_value=5, max_value=50, value=10)
artist_filter = st.sidebar.text_input("Filter Top Tracks by Artist (exact name)")

# Metrics
total_hours = df['hours'].sum()
total_tracks = len(df[df['ms_played'] > 0])
avg_listen_time = df[df['ms_played'] > 0]['hours'].mean()

st.title("🎧 Your Ultimate Spotify Wrapped Dashboard")

st.metric("Total Listening Hours", f"{total_hours:.2f}")
st.metric("Total Tracks Played", total_tracks)
st.metric("Average Listen Time (hours)", f"{avg_listen_time:.2f}")

# Top N Tracks
st.subheader(f"🎵 Top {top_n} Tracks")
top_tracks = (df[df['ms_played'] > 0]
              .groupby('master_metadata_track_name')['hours']
              .sum()
              .sort_values(ascending=False)
              .head(top_n)
              .reset_index())
top_tracks.columns = ['Track', 'Hours']
top_tracks['Hours'] = top_tracks['Hours'].round(2)
st.dataframe(top_tracks)


# Top N Tracks by Artist
if artist_filter:
    st.subheader(f"🎤 Top {top_n} Tracks by {artist_filter}")
    artist_df = df[df['master_metadata_album_artist_name'] == artist_filter]
    top_artist_tracks = (artist_df.groupby('master_metadata_track_name')['hours']
                         .sum()
                         .sort_values(ascending=False)
                         .head(top_n)
                         .reset_index())
    st.dataframe(top_artist_tracks)


# Platform Comparison
st.subheader("🖥️ Platform Usage Comparison")
# Group and rename columns
platform_usage = df.groupby('platform_clean')['minutes'].sum().sort_values(ascending=False).reset_index()
platform_usage.columns = ['Platform', 'Minutes']
# Correct column names in the plot
fig_platform = px.bar(platform_usage, x='Platform', y='Minutes', title="Minutes Played by Platform")
st.plotly_chart(fig_platform)


# Shuffle vs Non-Shuffle
st.subheader("🔀 Shuffle Usage")
shuffle_counts = df['shuffle'].value_counts().rename(index={True: "Shuffled", False: "Not Shuffled"}).reset_index()
shuffle_counts.columns = ['Shuffle', 'Count']
fig_shuffle = px.pie(shuffle_counts, names='Shuffle', values='Count', title="Shuffle vs Non-Shuffle")
st.plotly_chart(fig_shuffle)

# Offline vs Online
st.subheader("📶 Offline vs Online Playback")
offline_counts = df['offline'].value_counts().rename(index={True: "Offline", False: "Online"}).reset_index()
offline_counts.columns = ['Mode', 'Count']
fig_offline = px.pie(offline_counts, names='Mode', values='Count', title="Offline vs Online")
st.plotly_chart(fig_offline)

# Map of Countries Played
st.subheader("🌍 Country-wise Listening")
country_counts = df['conn_country_full'].value_counts().reset_index()
country_counts.columns = ['Country', 'Count']
fig_map = px.choropleth(country_counts, locations="Country", locationmode="country names",
                        color="Count", title="Music Played Around the World")
st.plotly_chart(fig_map)

# Line chart of playtime
st.subheader("📈 Listening Time Over Time")
time_series = df.groupby('date')['minutes'].sum().reset_index()
fig_time = px.line(time_series, x='date', y='minutes', title="Daily Listening Time")
st.plotly_chart(fig_time)
