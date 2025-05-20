import streamlit as st
import pandas as pd
import json
import glob
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import numpy as np

# Set page config
st.set_page_config(
    page_title="Spotify Listening Analysis",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1DB954;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #191414;
        margin-top: 1.5rem;
    }
    .stat-container {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 1rem;
        text-align: center;
    }
    .big-number {
        font-size: 2rem;
        font-weight: bold;
        color: #1DB954;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 class='main-header'>Spotify Listening Analysis</h1>", unsafe_allow_html=True)

# Function to load data
@st.cache_data
def load_data():
    """Load and process Spotify streaming history data"""
    # Load video data
    try:
        with open('Streaming_History_Video_2021-2025.json', 'r', encoding='utf-8') as f:
            video_data = pd.DataFrame(json.load(f))
        video_data['content_type'] = 'Video'
    except Exception as e:
        st.warning(f"Error loading video data: {e}")
        video_data = pd.DataFrame()
    
    # Load audio data from multiple files
    audio_files = glob.glob('Streaming_History_Audio_*.json')
    audio_dfs = []
    
    for file in audio_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                df = pd.DataFrame(json.load(f))
                audio_dfs.append(df)
        except Exception as e:
            st.warning(f"Error loading {file}: {e}")
    
    if audio_dfs:
        audio_data = pd.concat(audio_dfs, ignore_index=True)
        audio_data['content_type'] = 'Audio'
    else:
        audio_data = pd.DataFrame()
    
    # Combine data if both exist
    if not audio_data.empty and not video_data.empty:
        combined_data = pd.concat([audio_data, video_data], ignore_index=True)
    elif not audio_data.empty:
        combined_data = audio_data.copy()
    elif not video_data.empty:
        combined_data = video_data.copy()
    else:
        st.error("No data could be loaded!")
        return None, None, None
    
    # Process timestamps
    combined_data['ts'] = pd.to_datetime(combined_data['ts'])
    combined_data['date'] = combined_data['ts'].dt.date
    combined_data['hour'] = combined_data['ts'].dt.hour
    combined_data['day_of_week'] = combined_data['ts'].dt.day_name()
    combined_data['month'] = combined_data['ts'].dt.month_name()
    combined_data['year'] = combined_data['ts'].dt.year
    
    # Add duration in minutes
    combined_data['duration_min'] = combined_data['ms_played'] / (1000 * 60)
    
    # Remove duplicates based on timestamp and track name (for audio)
    if 'master_metadata_track_name' in combined_data.columns:
        audio_dedup = combined_data[combined_data['content_type'] == 'Audio'].drop_duplicates(
            subset=['ts', 'master_metadata_track_name', 'ms_played']
        )
    else:
        audio_dedup = combined_data[combined_data['content_type'] == 'Audio']
    
    # Remove duplicates for video content
    if 'episode_name' in combined_data.columns:
        video_dedup = combined_data[combined_data['content_type'] == 'Video'].drop_duplicates(
            subset=['ts', 'episode_name', 'ms_played']
        )
    else:
        video_dedup = combined_data[combined_data['content_type'] == 'Video']
    
    # Recombine deduplicated data
    dedup_data = pd.concat([audio_dedup, video_dedup], ignore_index=True)
    
    return combined_data, audio_dedup, video_dedup

# Load data
with st.spinner("Loading Spotify data... (this may take a moment)"):
    data, audio_data, video_data = load_data()

if data is not None:
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Year filter
    years = sorted(data['year'].unique())
    selected_years = st.sidebar.multiselect(
        "Select Years",
        options=years,
        default=years
    )
    
    # Content type filter
    content_types = sorted(data['content_type'].unique())
    selected_content = st.sidebar.multiselect(
        "Content Type",
        options=content_types,
        default=content_types
    )
    
    # Apply filters
    filtered_data = data[
        (data['year'].isin(selected_years)) & 
        (data['content_type'].isin(selected_content))
    ]
    
    # Top stats
    st.markdown("<h2 class='sub-header'>Overall Listening Stats</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='stat-container'>", unsafe_allow_html=True)
        st.markdown("<p>Total Listening Time</p>", unsafe_allow_html=True)
        hours = filtered_data['ms_played'].sum() / (1000 * 60 * 60)
        st.markdown(f"<p class='big-number'>{hours:.1f} hours</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='stat-container'>", unsafe_allow_html=True)
        st.markdown("<p>Total Tracks/Episodes</p>", unsafe_allow_html=True)
        total_items = len(filtered_data)
        st.markdown(f"<p class='big-number'>{total_items:,}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='stat-container'>", unsafe_allow_html=True)
        st.markdown("<p>Unique Days Active</p>", unsafe_allow_html=True)
        unique_days = filtered_data['date'].nunique()
        st.markdown(f"<p class='big-number'>{unique_days}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='stat-container'>", unsafe_allow_html=True)
        st.markdown("<p>Avg. Daily Listening</p>", unsafe_allow_html=True)
        avg_daily = hours / unique_days
        st.markdown(f"<p class='big-number'>{avg_daily:.1f} hours</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Time analysis section
    st.markdown("<h2 class='sub-header'>Listening Patterns</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly distribution
        hourly_data = filtered_data.groupby('hour')['ms_played'].sum() / (1000 * 60 * 60)
        hourly_fig = px.bar(
            x=hourly_data.index,
            y=hourly_data.values,
            labels={'x': 'Hour of Day', 'y': 'Hours'},
            title='Listening by Hour of Day',
            color_discrete_sequence=['#1DB954']
        )
        hourly_fig.update_layout(height=350)
        st.plotly_chart(hourly_fig, use_container_width=True)
    
    with col2:
        # Day of week distribution
        dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_data = filtered_data.groupby('day_of_week')['ms_played'].sum().reindex(dow_order) / (1000 * 60 * 60)
        dow_fig = px.bar(
            x=dow_data.index,
            y=dow_data.values,
            labels={'x': 'Day of Week', 'y': 'Hours'},
            title='Listening by Day of Week',
            color_discrete_sequence=['#1DB954']
        )
        dow_fig.update_layout(height=350)
        st.plotly_chart(dow_fig, use_container_width=True)
    
    # Monthly trend
    monthly_data = filtered_data.groupby(['year', filtered_data['ts'].dt.month])['ms_played'].sum() / (1000 * 60 * 60)
    monthly_data = monthly_data.reset_index()
    monthly_data['month_name'] = monthly_data['ts'].apply(lambda x: datetime(2000, x, 1).strftime('%b'))
    monthly_data['period'] = monthly_data['year'].astype(str) + '-' + monthly_data['month_name']
    
    monthly_fig = px.line(
        monthly_data, 
        x='period', 
        y='ms_played',
        markers=True,
        labels={'period': 'Month', 'ms_played': 'Hours'},
        title='Monthly Listening Trends',
        color_discrete_sequence=['#1DB954']
    )
    monthly_fig.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(monthly_fig, use_container_width=True)
    
    # Content Analysis
    st.markdown("<h2 class='sub-header'>Content Analysis</h2>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Audio Content", "Video Content"])
    
    with tab1:
        if not audio_data.empty and 'master_metadata_album_artist_name' in audio_data.columns:
            st.subheader("Top Artists")
            
            # Filter audio data with the same filters
            filtered_audio = audio_data[
                (audio_data['year'].isin(selected_years))
            ]
            
            # Top artists
            top_artists = filtered_audio.groupby('master_metadata_album_artist_name')['ms_played'].sum().nlargest(10)
            artist_fig = px.bar(
                y=top_artists.index,
                x=top_artists.values / (1000 * 60 * 60),
                labels={'y': 'Artist', 'x': 'Hours'},
                title='Top 10 Artists by Listening Time',
                orientation='h',
                color_discrete_sequence=['#1DB954']
            )
            st.plotly_chart(artist_fig, use_container_width=True)
            
            # Top tracks
            if 'master_metadata_track_name' in filtered_audio.columns:
                st.subheader("Top Tracks")
                top_tracks = filtered_audio.groupby('master_metadata_track_name')['ms_played'].sum().nlargest(10)
                track_fig = px.bar(
                    y=top_tracks.index,
                    x=top_tracks.values / (1000 * 60),
                    labels={'y': 'Track', 'x': 'Minutes'},
                    title='Top 10 Tracks by Listening Time',
                    orientation='h',
                    color_discrete_sequence=['#1DB954']
                )
                st.plotly_chart(track_fig, use_container_width=True)
        else:
            st.info("No audio data available for analysis or required fields missing.")
    
    with tab2:
        if not video_data.empty and 'episode_show_name' in video_data.columns:
            st.subheader("Top Shows")
            
            # Filter video data with the same filters
            filtered_video = video_data[
                (video_data['year'].isin(selected_years))
            ]
            
            # Top shows
            top_shows = filtered_video.groupby('episode_show_name')['ms_played'].sum().nlargest(10)
            show_fig = px.bar(
                y=top_shows.index,
                x=top_shows.values / (1000 * 60 * 60),
                labels={'y': 'Show', 'x': 'Hours'},
                title='Top 10 Shows by Watching Time',
                orientation='h',
                color_discrete_sequence=['#1DB954']
            )
            st.plotly_chart(show_fig, use_container_width=True)
            
            # Top episodes
            if 'episode_name' in filtered_video.columns:
                st.subheader("Top Episodes")
                top_episodes = filtered_video.groupby('episode_name')['ms_played'].sum().nlargest(10)
                episode_fig = px.bar(
                    y=top_episodes.index,
                    x=top_episodes.values / (1000 * 60),
                    labels={'y': 'Episode', 'x': 'Minutes'},
                    title='Top 10 Episodes by Watching Time',
                    orientation='h',
                    color_discrete_sequence=['#1DB954']
                )
                st.plotly_chart(episode_fig, use_container_width=True)
        else:
            st.info("No video data available for analysis or required fields missing.")
    
    # Platform Analysis
    st.markdown("<h2 class='sub-header'>Platform Usage Analysis</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Platform distribution
        platform_data = filtered_data.groupby('platform')['ms_played'].sum().nlargest(10)
        platform_fig = px.pie(
            values=platform_data.values,
            names=platform_data.index,
            title='Listening Time by Platform',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(platform_fig, use_container_width=True)
    
    with col2:
        # Shuffle usage if available
        if 'shuffle' in filtered_data.columns:
            shuffle_data = filtered_data.groupby('shuffle')['ms_played'].sum()
            shuffle_fig = px.pie(
                values=shuffle_data.values,
                names=shuffle_data.index,
                title='Shuffle vs Sequential Listening',
                hole=0.4,
                color_discrete_sequence=['#1DB954', '#191414']
            )
            st.plotly_chart(shuffle_fig, use_container_width=True)
        else:
            st.info("Shuffle data not available.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center;">
        <p>Dashboard created from Spotify Streaming History data</p>
        <p style="font-size: 0.8rem;">Tip: You can download any chart by hovering over it and clicking the download button</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("Failed to load data. Please check your data files.")

# Instructions for running
if not st.sidebar.checkbox("Hide Instructions", value=False):
    st.sidebar.markdown("## How to Run")
    st.sidebar.markdown("""
    1. Install requirements:
    ```
    pip install -r requirements.txt
    ```
    
    2. Run the dashboard:
    ```
    streamlit run spotify_dashboard.py
    ```
    """) 