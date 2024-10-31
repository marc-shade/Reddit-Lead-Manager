import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from lead_manager import LeadManager
from storage import LocalStorage
from analytics import AnalyticsManager
import json
import io

def convert_to_serializable(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def export_lead_status_report(lead_manager, analytics):
    """Generate lead status report CSV"""
    df = lead_manager.get_leads()
    if df is None or df.empty:
        return None
        
    # Get analytics data
    conversion_rates = analytics.get_conversion_rates()
    response_stats = analytics.get_response_stats()
    
    # Create summary stats
    summary_data = {
        'Total Leads': len(df),
        'New Leads': len(df[df['status'] == 'New']),
        'In Progress': len(df[df['status'] == 'In Progress']),
        'Contacted': len(df[df['status'] == 'Contacted']),
        'Closed': len(df[df['status'] == 'Closed']),
        'New to Progress Rate': f"{conversion_rates['new_to_progress']:.1f}%",
        'Progress to Contacted Rate': f"{conversion_rates['progress_to_contacted']:.1f}%",
        'Contacted to Closed Rate': f"{conversion_rates['contacted_to_closed']:.1f}%",
        'Leads with Notes': response_stats['leads_with_notes'],
        'Notes Coverage': f"{response_stats['notes_percentage']:.1f}%",
        'Report Generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Convert to DataFrame
    summary_df = pd.DataFrame(list(summary_data.items()), columns=['Metric', 'Value'])
    return summary_df

def export_detailed_leads(lead_manager):
    """Export detailed lead data"""
    df = lead_manager.get_leads()
    if df is None or df.empty:
        return None
    return df

def export_analytics_summary(analytics):
    """Export analytics summary as JSON"""
    summary = {
        'status_distribution': analytics.get_status_distribution(),
        'subreddit_distribution': analytics.get_subreddit_distribution(),
        'daily_activity': analytics.get_daily_activity(),
        'conversion_rates': analytics.get_conversion_rates(),
        'response_stats': analytics.get_response_stats(),
        'funnel_data': analytics.get_funnel_data()
    }
    
    # Convert numpy types to native Python types
    def convert_nested_dict(d):
        if isinstance(d, dict):
            return {k: convert_nested_dict(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [convert_nested_dict(item) for item in d]
        return convert_to_serializable(d)
    
    return convert_nested_dict(summary)

def main():
    st.set_page_config(
        page_title="Lead Analytics",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Lead Management Analytics")

    # Initialize components
    storage = LocalStorage()
    lead_manager = LeadManager(storage)
    analytics = AnalyticsManager(lead_manager)

    # Export Section
    st.sidebar.header("Export Options")
    
    # Lead Status Report
    status_report = export_lead_status_report(lead_manager, analytics)
    if status_report is not None:
        status_csv = status_report.to_csv(index=False)
        st.sidebar.download_button(
            "📥 Download Status Report",
            status_csv,
            "lead_status_report.csv",
            "text/csv",
            key='status_report'
        )

    # Detailed Lead Data
    detailed_data = export_detailed_leads(lead_manager)
    if detailed_data is not None:
        detailed_csv = detailed_data.to_csv(index=False)
        st.sidebar.download_button(
            "📥 Download Detailed Lead Data",
            detailed_csv,
            "detailed_leads.csv",
            "text/csv",
            key='detailed_data'
        )

    # Analytics Summary
    analytics_summary = export_analytics_summary(analytics)
    if analytics_summary:
        analytics_json = json.dumps(analytics_summary, indent=2)
        st.sidebar.download_button(
            "📥 Download Analytics Summary",
            analytics_json,
            "analytics_summary.json",
            "application/json",
            key='analytics_summary'
        )

    # Get analytics data
    status_dist = analytics.get_status_distribution()
    subreddit_dist = analytics.get_subreddit_distribution()
    daily_activity = analytics.get_daily_activity()
    conversion_rates = analytics.get_conversion_rates()
    response_stats = analytics.get_response_stats()
    funnel_data = analytics.get_funnel_data()

    if not status_dist['labels']:
        st.warning("No lead data available. Please sync leads from the main page.")
        return

    # Create layout with columns
    col1, col2 = st.columns(2)

    # Status Distribution (Left column)
    with col1:
        st.subheader("Lead Status Distribution")
        fig = go.Figure(data=[go.Pie(
            labels=status_dist['labels'],
            values=status_dist['values'],
            hole=.3,
            marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        )])
        fig.update_layout(margin=dict(t=0, b=0), height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Lead Funnel (Right column)
    with col2:
        st.subheader("Lead Progression Funnel")
        if funnel_data:
            funnel_values = [d['count'] for d in funnel_data]
            funnel_labels = [f"{d['status']}<br>{d['count']} leads ({d['percentage']:.1f}%)" 
                           for d in funnel_data]
            
            fig = go.Figure(data=[go.Funnel(
                y=funnel_labels,
                x=funnel_values,
                textposition="inside",
                textinfo="value+percent previous",
                opacity=0.85,
                marker={
                    "color": ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],
                    "line": {"width": 2, "color": "white"}
                },
                connector={"line": {"color": "grey", "dash": "dot", "width": 1}}
            )])
            
            fig.update_layout(margin=dict(t=0, b=0), height=300)
            st.plotly_chart(fig, use_container_width=True)

    # Subreddit Distribution
    st.subheader("Top Subreddits by Lead Count")
    if subreddit_dist['labels']:
        fig = px.bar(
            x=subreddit_dist['labels'],
            y=subreddit_dist['values'],
            labels={'x': 'Subreddit', 'y': 'Number of Leads'},
            color_discrete_sequence=['#1f77b4']
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            margin=dict(t=0, b=0),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

    # Daily Activity
    st.subheader("Daily Lead Activity (Last 30 Days)")
    if daily_activity['dates']:
        fig = px.line(
            x=daily_activity['dates'],
            y=daily_activity['counts'],
            labels={'x': 'Date', 'y': 'Number of Leads'},
            line_shape='linear'
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            margin=dict(t=0, b=0),
            showlegend=False,
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

    # Metrics Section
    st.subheader("Performance Metrics")
    
    # Conversion Metrics
    cols = st.columns(3)
    metrics = [
        ("New → In Progress", 'new_to_progress'),
        ("In Progress → Contacted", 'progress_to_contacted'),
        ("Contacted → Closed", 'contacted_to_closed')
    ]
    
    for col, (label, key) in zip(cols, metrics):
        with col:
            value = conversion_rates.get(key, 0)
            st.metric(
                label,
                f"{value:.1f}%"
            )

    # Response Stats
    st.markdown("##### Response Statistics")
    cols = st.columns(3)
    
    with cols[0]:
        st.metric(
            "Leads with Notes",
            f"{response_stats['leads_with_notes']:,}"
        )
    
    with cols[1]:
        st.metric(
            "Notes Coverage",
            f"{response_stats['notes_percentage']:.1f}%"
        )
    
    with cols[2]:
        st.metric(
            "Avg. Notes Length",
            f"{response_stats['avg_notes_length']:.0f} chars"
        )

if __name__ == "__main__":
    main()
