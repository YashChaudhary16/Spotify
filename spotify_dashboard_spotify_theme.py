import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import requests
pio.json.config.default_engine = "json"

# Custom theme configuration
st.set_page_config(
    page_title="Spotify Wrapped Dashboard",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #121212;
        color: #FFFFFF;
    }
    .stMetric {
        background-color: #282828;
        padding: 20px;
        border-radius: 10px;
    }
    .stMetric label {
        color: #B3B3B3;
    }
    .stMetric div {
        color: #FFFFFF;
    }
    .stSubheader {
        color: #1DB954;
    }
    .stDataFrame {
        background-color: #282828;
    }
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #121212;
    }
    .sidebar .sidebar-content {
        background-color: #121212;
    }
    .stSidebar {
        background-color: #121212;
    }
    .sidebar-header {
        color: #1DB954;
        font-size: 24px;
        font-weight: bold;
        padding: 20px 0;
        text-align: center;
        border-bottom: 2px solid #282828;
        margin-bottom: 20px;
    }
    .sidebar-section {
        background-color: #282828;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .sidebar-section-title {
        color: #1DB954;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

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
df['Year'] = pd.to_datetime(df['ts_local_clean']).dt.year

# Enhanced Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-header">🎧 Spotify Analytics</div>', unsafe_allow_html=True)
    
    # Time Range Selection with checkboxes
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">📅 Time Range</div>', unsafe_allow_html=True)
    all_years = sorted(df['Year'].dropna().unique())
    year_checks = {}
    for year in all_years:
        year_checks[year] = st.checkbox(str(year), value=True, key=f"year_{year}")
    selected_years = [year for year, checked in year_checks.items() if checked]
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Track Analysis with number input
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">🎵 Track Analysis</div>', unsafe_allow_html=True)
    top_n = st.number_input(
        "Number of Top Tracks",
        min_value=5,
        max_value=50,
        value=10,
        step=1,
        help="Enter how many top tracks to display"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Artist Analysis with autocomplete
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">🎤 Artist Analysis</div>', unsafe_allow_html=True)
    artist_list = sorted(df['master_metadata_album_artist_name'].dropna().unique())
    artist_filter = st.selectbox(
        "Select or Search Artist",
        options=["(All Artists)"] + artist_list,
        index=0,
        help="Start typing to search for an artist"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # About Section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">ℹ️ About</div>', unsafe_allow_html=True)
    st.markdown("""
        This dashboard provides detailed analytics of your Spotify listening history.
        Use the filters above to customize your view.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Filter by selected years
if selected_years:
    df = df[df['Year'].isin(selected_years)]

# Metrics
total_hours = df['hours'].sum()
total_tracks = len(df[df['ms_played'] > 0])

# Total number of unique listening days
unique_days = df['date'].nunique()

# Average listening hours per day
avg_hours_per_day = total_hours / unique_days if unique_days > 0 else 0

# Format average listen time
h = int(avg_hours_per_day)
m = int(round((avg_hours_per_day - h) * 60))
formatted_avg = f"{h} hrs {m} mins"

st.title("🎧 Your Ultimate Spotify Wrapped Dashboard")

# Create three columns for metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Listening Hours", f"{total_hours:.2f}", 
              help="Total hours spent listening to music")
with col2:
    st.metric("Total Tracks Played", f"{total_tracks:,}", 
              help="Total number of unique tracks played")
with col3:
    st.metric("Average Listen Time", formatted_avg,
              help="Average listening time per day")

# Add a divider
st.markdown("---")

# Top N Tracks
st.subheader(f"🎵 Top {top_n} Tracks")
top_tracks = (df[df['ms_played'] > 0]
              .groupby('master_metadata_track_name')['hours']
              .sum()
              .sort_values(ascending=False)
              .head(top_n)
              .reset_index())
top_tracks.columns = ['Track', 'Hours']
top_tracks['Listening Time'] = top_tracks['Hours'].apply(
    lambda h: f"{int(h)} hrs {int(round((h - int(h)) * 60))} mins"
)
top_tracks = top_tracks[['Track', 'Listening Time']]
st.dataframe(top_tracks)

# Top N Tracks by Artist
# if artist_filter and artist_filter != "(All Artists)":
#     st.subheader(f"🎤 Top {top_n} Tracks by {artist_filter}")
#     artist_df = df[df['master_metadata_album_artist_name'] == artist_filter]
#     top_artist_tracks = (artist_df.groupby('master_metadata_track_name')['hours']
#                          .sum()
#                          .sort_values(ascending=False)
#                          .head(top_n)
#                          .reset_index())
#     top_artist_tracks.columns = ['Track', 'Hours']
#     top_artist_tracks['Listening Time'] = top_artist_tracks['Hours'].apply(
#         lambda h: f"{int(h)} hrs {int(round((h - int(h)) * 60))} mins"
#     )
#     top_artist_tracks = top_artist_tracks[['Track', 'Listening Time']]
#     st.dataframe(top_artist_tracks)

# Platform Comparison
st.subheader("🖥️ Platform Usage Comparison")
platform_usage = df.groupby('platform_clean')['hours'].sum().sort_values(ascending=False).reset_index()
platform_usage.columns = ['Platform', 'Hours']
platform_usage['Hours'] = platform_usage['Hours'].round(2)
fig_platform = px.bar(platform_usage, x='Platform', y='Hours', 
                      title="Hours Played by Platform",
                      color_discrete_sequence=['#1db954'],
                      template='plotly_dark')
fig_platform.update_layout(
    plot_bgcolor='#282828',
    paper_bgcolor='#282828',
    font=dict(color='white'),
    hovermode='x unified'
)
st.plotly_chart(fig_platform, use_container_width=True)

# Create two columns for pie charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔀 Shuffle Usage")
    shuffle_counts = df['shuffle'].value_counts().rename(index={True: "Shuffled", False: "Not Shuffled"}).reset_index()
    shuffle_counts.columns = ['Shuffle', 'Count']
    fig_shuffle = px.pie(shuffle_counts, names='Shuffle', values='Count', 
                        title="Shuffle vs Non-Shuffle",
                        color_discrete_sequence=['#1db954', '#212121'],
                        template='plotly_dark')
    fig_shuffle.update_layout(
        plot_bgcolor='#282828',
        paper_bgcolor='#282828',
        font=dict(color='white')
    )
    st.plotly_chart(fig_shuffle, use_container_width=True)

with col2:
    st.subheader("📶 Offline vs Online Playback")
    offline_counts = df['offline'].value_counts().rename(index={True: "Offline", False: "Online"}).reset_index()
    offline_counts.columns = ['Mode', 'Count']
    fig_offline = px.pie(offline_counts, names='Mode', values='Count', 
                        title="Offline vs Online",
                        color_discrete_sequence=['#1db954', '#121212'],
                        template='plotly_dark')
    fig_offline.update_layout(
        plot_bgcolor='#282828',
        paper_bgcolor='#282828',
        font=dict(color='white')
    )
    st.plotly_chart(fig_offline, use_container_width=True)

# Map of Countries Played
st.subheader("🌍 Country-wise Listening")
country_counts = df.groupby('conn_country_full')['hours'].sum().round(2).reset_index()
country_counts.columns = ['Country', 'Hours']
fig_map = px.choropleth(country_counts, 
                       locations="Country", 
                       locationmode="country names",
                       color="Hours", 
                       title="Hours of Music Played Around the World",
                       color_continuous_scale=['#121212', '#1db954'],
                       template='plotly_dark')
fig_map.update_layout(
    plot_bgcolor='#282828',
    paper_bgcolor='#282828',
    font=dict(color='white'),
    geo=dict(bgcolor='#282828')
)
st.plotly_chart(fig_map, use_container_width=True)

# Line chart of playtime
st.subheader("📈 Listening Time Over Time")
time_series = df.groupby('date')['hours'].sum().round(2).reset_index()
fig_time = px.line(time_series, x='date', y='hours', 
                  title="Daily Listening Time (Hours)",
                  color_discrete_sequence=['#1db954'],
                  template='plotly_dark')
fig_time.update_layout(
    plot_bgcolor='#282828',
    paper_bgcolor='#282828',
    font=dict(color='white'),
    hovermode='x unified',
    xaxis=dict(
        showgrid=True,
        gridcolor='#404040'
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='#404040'
    )
)
st.plotly_chart(fig_time, use_container_width=True)

# Artist-specific Analytics
st.subheader("🎤 Artist Analytics")
if artist_filter and artist_filter != "(All Artists)":
    # Display artist image from Wikipedia
    def get_artist_image(artist_name):
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&titles={artist_name}&pithumbsize=300"
        try:
            resp = requests.get(url, timeout=5)
            data = resp.json()
            pages = data['query']['pages']
            for page in pages.values():
                if 'thumbnail' in page:
                    return page['thumbnail']['source']
        except Exception:
            return None
        return None
    artist_img_url = get_artist_image(artist_filter)
    if artist_img_url:
        st.image(artist_img_url, caption=artist_filter, width=200)
    else:
        st.info(f"No image found for {artist_filter}.")

    artist_df = df[df['master_metadata_album_artist_name'] == artist_filter]
    
    # Artist-specific metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        artist_hours = artist_df['hours'].sum().round(2)
        st.metric(f"Total Hours Listening to {artist_filter}", f"{artist_hours:.2f}")
    with col2:
        artist_tracks = len(artist_df['master_metadata_track_name'].unique())
        st.metric(f"Unique Tracks by {artist_filter}", artist_tracks)
    with col3:
        artist_avg_hours = artist_hours / unique_days if unique_days > 0 else 0
        st.metric(f"Average Daily Hours of {artist_filter}", f"{artist_avg_hours:.2f}")
    
    # Artist's top tracks
    # st.subheader(f"🎵 Top {int(top_n)} Tracks by {artist_filter}")
    # top_artist_tracks = (artist_df.groupby('master_metadata_track_name')['hours']
    #                     .sum()
    #                     .sort_values(ascending=False)
    #                     .head(int(top_n))
    #                     .reset_index())
    # top_artist_tracks.columns = ['Track', 'Hours']
    # top_artist_tracks['Hours'] = top_artist_tracks['Hours'].round(2)
    # st.dataframe(top_artist_tracks)

    st.subheader(f"🎤 Top {top_n} Tracks by {artist_filter}")
    artist_df = df[df['master_metadata_album_artist_name'] == artist_filter]
    top_artist_tracks = (artist_df.groupby('master_metadata_track_name')['hours']
                         .sum()
                         .sort_values(ascending=False)
                         .head(top_n)
                         .reset_index())
    top_artist_tracks.columns = ['Track', 'Hours']
    top_artist_tracks['Listening Time'] = top_artist_tracks['Hours'].apply(
        lambda h: f"{int(h)} hrs {int(round((h - int(h)) * 60))} mins"
    )
    top_artist_tracks = top_artist_tracks[['Track', 'Listening Time']]
    st.dataframe(top_artist_tracks)

    # Artist's listening time over time
    st.subheader(f"📈 {artist_filter} Listening Time Over Time")
    artist_time_series = artist_df.groupby('date')['hours'].sum().round(2).reset_index()
    fig_artist_time = px.line(artist_time_series, x='date', y='hours',
                             title=f"Daily {artist_filter} Listening Time (Hours)",
                             color_discrete_sequence=['#1db954'],
                             template='plotly_dark')
    fig_artist_time.update_layout(
        plot_bgcolor='#282828',
        paper_bgcolor='#282828',
        font=dict(color='white'),
        hovermode='x unified',
        xaxis=dict(showgrid=True, gridcolor='#404040'),
        yaxis=dict(showgrid=True, gridcolor='#404040')
    )
    st.plotly_chart(fig_artist_time, use_container_width=True)
    
    # Artist's platform usage
    st.subheader(f"🖥️ {artist_filter} Platform Usage")
    artist_platform = artist_df.groupby('platform_clean')['hours'].sum().round(2).reset_index()
    artist_platform.columns = ['Platform', 'Hours']
    fig_artist_platform = px.bar(artist_platform, x='Platform', y='Hours',
                                title=f"Hours of {artist_filter} Played by Platform",
                                color_discrete_sequence=['#1db954'],
                                template='plotly_dark')
    fig_artist_platform.update_layout(
        plot_bgcolor='#282828',
        paper_bgcolor='#282828',
        font=dict(color='white'),
        hovermode='x unified'
    )
    st.plotly_chart(fig_artist_platform, use_container_width=True)

    # Artist's shuffle comparison
    st.subheader(f"🔀 {artist_filter} Shuffle Usage")
    shuffle_counts = artist_df['shuffle'].value_counts().rename(index={True: "Shuffled", False: "Not Shuffled"}).reset_index()
    shuffle_counts.columns = ['Shuffle', 'Count']
    fig_shuffle = px.pie(shuffle_counts, names='Shuffle', values='Count',
                        title=f"Shuffle vs Non-Shuffle for {artist_filter}",
                        color_discrete_sequence=['#1db954', '#212121'],
                        template='plotly_dark')
    fig_shuffle.update_layout(
        plot_bgcolor='#282828',
        paper_bgcolor='#282828',
        font=dict(color='white')
    )
    st.plotly_chart(fig_shuffle, use_container_width=True)

    # Artist's offline/online comparison
    st.subheader(f"📶 {artist_filter} Offline vs Online Playback")
    offline_counts = artist_df['offline'].value_counts().rename(index={True: "Offline", False: "Online"}).reset_index()
    offline_counts.columns = ['Mode', 'Count']
    fig_offline = px.pie(offline_counts, names='Mode', values='Count',
                        title=f"Offline vs Online for {artist_filter}",
                        color_discrete_sequence=['#1db954', '#121212'],
                        template='plotly_dark')
    fig_offline.update_layout(
        plot_bgcolor='#282828',
        paper_bgcolor='#282828',
        font=dict(color='white')
    )
    st.plotly_chart(fig_offline, use_container_width=True)

    # Artist's country-wise listening
    st.subheader(f"🌍 {artist_filter} Country-wise Listening")
    artist_country_counts = artist_df.groupby('conn_country_full')['hours'].sum().round(2).reset_index()
    artist_country_counts.columns = ['Country', 'Hours']
    fig_artist_map = px.choropleth(artist_country_counts,
                                   locations="Country",
                                   locationmode="country names",
                                   color="Hours",
                                   title=f"Hours of {artist_filter} Played Around the World",
                                   color_continuous_scale=['#121212', '#1db954'],
                                   template='plotly_dark')
    fig_artist_map.update_layout(
        plot_bgcolor='#282828',
        paper_bgcolor='#282828',
        font=dict(color='white'),
        geo=dict(bgcolor='#282828')
    )
    st.plotly_chart(fig_artist_map, use_container_width=True)

# --- Feature 1: Listening Streaks ---
df_sorted = df.sort_values('date')
activity_days = pd.Series(df_sorted['date'].unique())
activity_days = pd.to_datetime(activity_days)
streaks = (activity_days.diff() != pd.Timedelta(days=1)).cumsum()
streak_lengths = activity_days.groupby(streaks).agg(['count', 'min', 'max'])
longest_streak = streak_lengths['count'].max()
longest_streak_row = streak_lengths[streak_lengths['count'] == longest_streak].iloc[0]
longest_streak_start = longest_streak_row['min'].date()
longest_streak_end = longest_streak_row['max'].date()

# Day with highest listening
max_day_row = df.groupby('date')['hours'].sum().sort_values(ascending=False).reset_index().iloc[0]
max_day = max_day_row['date']
max_day_hours = max_day_row['hours']

# --- Feature 4: Listening Milestones ---
first_row = df.sort_values('ts_local_clean').iloc[0]
first_song = first_row['master_metadata_track_name']
first_artist = first_row['master_metadata_album_artist_name']
first_date = first_row['date']

# Cumulative hours for milestones
cumulative = df.groupby('date')['hours'].sum().cumsum().reset_index()
milestones = [100, 500, 1000, 2000, 5000, 10000, 20000]
milestone_dates = {}
for m in milestones:
    milestone_row = cumulative[cumulative['hours'] >= m].head(1)
    if not milestone_row.empty:
        milestone_dates[m] = milestone_row.iloc[0]['date']

# Most listened track and date
track_hours = df.groupby('master_metadata_track_name')['hours'].sum().sort_values(ascending=False)
most_listened_track = track_hours.index[0]
most_listened_hours = track_hours.iloc[0]
most_listened_date = df[df['master_metadata_track_name'] == most_listened_track].groupby('date')['hours'].sum().idxmax()

# --- Feature 5: Listening by Time of Day ---
df['hour'] = pd.to_datetime(df['ts_local_clean']).dt.hour
def time_bucket(h):
    if 5 <= h <= 11:
        return 'Morning (5-11)'
    elif 12 <= h <= 17:
        return 'Afternoon (12-17)'
    elif 18 <= h <= 22:
        return 'Evening (18-22)'
    else:
        return 'Night (23-4)'
df['time_bucket'] = df['hour'].apply(time_bucket)
time_of_day = df.groupby('time_bucket')['hours'].sum().reindex([
    'Morning (5-11)', 'Afternoon (12-17)', 'Evening (18-22)', 'Night (23-4)']).reset_index()

# --- Feature 7: Skips and Replays Insight ---
total_skipped = df['skipped'].sum() if 'skipped' in df.columns else 0
top_skipped = (df[df['skipped'] == True]
               .groupby('master_metadata_track_name')
               .size()
               .sort_values(ascending=False)
               .head(5)
               .reset_index(name='Skips')) if 'skipped' in df.columns else pd.DataFrame()
top_played = (df[df['skipped'] == False]
              .groupby('master_metadata_track_name')['hours']
              .sum()
              .sort_values(ascending=False)
              .head(5)
              .reset_index()) if 'skipped' in df.columns else pd.DataFrame()

# --- Custom Feature: Monthly and Weekday Trends ---
df['month'] = pd.to_datetime(df['ts_local_clean']).dt.strftime('%b')
df['month_num'] = pd.to_datetime(df['ts_local_clean']).dt.month
df['weekday'] = pd.to_datetime(df['ts_local_clean']).dt.day_name()
monthly_hours = df.groupby(['month_num', 'month'])['hours'].sum().reset_index().sort_values('month_num')

# FIX: Average daily listening hours by weekday (use daily totals)
daily_totals = df.groupby('date')['hours'].sum().reset_index()
daily_totals['weekday'] = pd.to_datetime(daily_totals['date']).dt.day_name()
weekday_hours = daily_totals.groupby('weekday')['hours'].mean().reindex([
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).reset_index()

# heatmap_data = df.groupby(['month', 'weekday'])['hours'].sum().unstack(fill_value=0)
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Apply Categorical type to preserve order
df['month'] = pd.Categorical(df['month'], categories=month_order, ordered=True)
df['weekday'] = pd.Categorical(df['weekday'], categories=weekday_order, ordered=True)

heatmap_data = df.groupby(['month', 'weekday'])['hours'].sum().unstack(fill_value=0).loc[month_order]


# --- UI Section: Listening Streaks and Milestones ---
st.markdown("## 🏆 Listening Streaks & Milestones")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Longest Listening Streak", f"{longest_streak} days", f"{longest_streak_start} → {longest_streak_end}")
with col2:
    st.metric("Day with Most Listening", f"{max_day_hours:.2f} hrs", f"{max_day}")
with col3:
    st.metric("First Song Played", f"{first_song}", f"{first_artist} ({first_date})")

# Milestones Timeline
st.markdown("### 🎉 Listening Milestones")
for m, d in milestone_dates.items():
    st.info(f"Crossed {m} hours on {d}")
st.success(f"Most Listened Track: {most_listened_track} ({most_listened_hours:.2f} hrs), Top Day: {most_listened_date}")

# --- UI Section: Listening by Time of Day ---
st.markdown("## ⏰ Listening by Time of Day")
fig_timeofday = px.bar(time_of_day, x='time_bucket', y='hours',
                      color='time_bucket',
                      color_discrete_sequence=['#1db954', '#b3b3b3', '#535353', '#191414'],
                      title="Total Listening Hours by Time of Day")
fig_timeofday.update_layout(showlegend=False, plot_bgcolor='#282828', paper_bgcolor='#282828', font=dict(color='white'))
st.plotly_chart(fig_timeofday, use_container_width=True)

# --- UI Section: Skips and Replays ---
st.markdown("## ⏭️ Skips and Replays Insight")
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Skipped Tracks", int(total_skipped))
    if not top_skipped.empty:
        st.dataframe(top_skipped, use_container_width=True)
with col2:
    st.metric("Top Played (Non-Skipped)", "")
    if not top_played.empty:
        st.dataframe(top_played, use_container_width=True)

# --- UI Section: Monthly and Weekday Trends ---
st.markdown("## 📅 Monthly and Weekday Listening Trends")
fig_month = px.bar(monthly_hours, x='month', y='hours',
                   title="Total Listening Hours per Month",
                   color_discrete_sequence=['#1db954'],
                   category_orders={'month': list(monthly_hours['month'])})
fig_month.update_layout(plot_bgcolor='#282828', paper_bgcolor='#282828', font=dict(color='white'))
st.plotly_chart(fig_month, use_container_width=True)

fig_weekday = px.bar(weekday_hours, x='weekday', y='hours',
                     title="Average Daily Listening Hours by Weekday",
                     color_discrete_sequence=['#1db954'],
                     category_orders={'weekday': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']})
fig_weekday.update_layout(plot_bgcolor='#282828', paper_bgcolor='#282828', font=dict(color='white'))
st.plotly_chart(fig_weekday, use_container_width=True)

fig_heatmap = px.imshow(heatmap_data,
                       labels=dict(x="Weekday", y="Month", color="Hours"),
                       x=heatmap_data.columns,
                       y=heatmap_data.index,
                       color_continuous_scale=['#121212', '#1db954'],
                       title="Listening Hours: Month vs. Weekday")
fig_heatmap.update_layout(plot_bgcolor='#282828', paper_bgcolor='#282828', font=dict(color='white'))
st.plotly_chart(fig_heatmap, use_container_width=True)

# --- Feature 14: Export Summary to PDF/PNG (Placeholder) ---
st.markdown("## 📤 Export Your Spotify Summary")
st.info("Export to PDF/PNG coming soon! (Will include total hours, top tracks, top artist, and streaks)")
# (Implementation would use pdfkit/imgkit/html2image and st.download_button)
