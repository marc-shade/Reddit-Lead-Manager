import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class AnalyticsManager:
    def __init__(self, lead_manager):
        self.lead_manager = lead_manager

    def get_status_distribution(self):
        """Get distribution of leads across different statuses"""
        df = self.lead_manager.get_leads()
        if df is None or df.empty:
            return {'labels': [], 'values': []}
            
        status_order = ['New', 'In Progress', 'Contacted', 'Closed']
        status_counts = df['status'].value_counts().reindex(status_order, fill_value=0)
        return {
            'labels': status_counts.index.tolist(),
            'values': status_counts.values.tolist()
        }

    def get_subreddit_distribution(self):
        """Get distribution of leads across subreddits"""
        df = self.lead_manager.get_leads()
        if df is None or df.empty:
            return {'labels': [], 'values': []}
            
        subreddit_counts = df['subreddit'].value_counts().nlargest(10)  # Show top 10 subreddits
        return {
            'labels': subreddit_counts.index.tolist(),
            'values': subreddit_counts.values.tolist()
        }

    def get_daily_activity(self, days=30):
        """Get daily lead activity for the past n days"""
        df = self.lead_manager.get_leads()
        
        if df is None or df.empty:
            return {'dates': [], 'counts': []}
            
        # Convert date strings to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Create date range
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Group by date and count
        daily_counts = df[df['date'].dt.date >= start_date.date()].groupby(
            df['date'].dt.date
        ).size().reindex(
            date_range.date,
            fill_value=0
        )
        
        return {
            'dates': [d.strftime('%Y-%m-%d') for d in daily_counts.index],
            'counts': daily_counts.values.tolist()
        }

    def get_funnel_data(self):
        """Get funnel data showing lead progression through statuses"""
        df = self.lead_manager.get_leads()
        if df is None or df.empty:
            return []
            
        total_leads = len(df)
        
        # Define status order
        status_order = ['New', 'In Progress', 'Contacted', 'Closed']
        status_counts = df['status'].value_counts()
        
        funnel_data = []
        cumulative_count = total_leads
        for status in status_order:
            count = status_counts.get(status, 0)
            percentage = (count / total_leads * 100) if total_leads > 0 else 0
            funnel_data.append({
                'status': status,
                'count': cumulative_count,
                'percentage': (cumulative_count / total_leads * 100) if total_leads > 0 else 0
            })
            cumulative_count -= count
        
        return funnel_data

    def get_conversion_rates(self):
        """Calculate conversion rates between statuses"""
        df = self.lead_manager.get_leads()
        if df is None or df.empty:
            return {
                'new_to_progress': 0,
                'progress_to_contacted': 0,
                'contacted_to_closed': 0
            }
            
        status_counts = df['status'].value_counts()
        
        def calculate_rate(from_status, to_status):
            from_count = status_counts.get(from_status, 0)
            to_count = status_counts.get(to_status, 0)
            return (to_count / from_count * 100) if from_count > 0 else 0
        
        return {
            'new_to_progress': calculate_rate('New', 'In Progress'),
            'progress_to_contacted': calculate_rate('In Progress', 'Contacted'),
            'contacted_to_closed': calculate_rate('Contacted', 'Closed')
        }

    def get_response_stats(self):
        """Calculate stats about notes and responses"""
        df = self.lead_manager.get_leads()
        
        if df is None or df.empty:
            return {
                'leads_with_notes': 0,
                'notes_percentage': 0,
                'avg_notes_length': 0
            }
        
        # Convert notes to string and handle NaN values
        df['notes'] = df['notes'].fillna('').astype(str)
        leads_with_notes = df[df['notes'].str.len() > 0].shape[0]
        notes_percentage = (leads_with_notes / len(df) * 100)
        avg_notes_length = df['notes'].str.len().mean() if leads_with_notes > 0 else 0
        
        return {
            'leads_with_notes': leads_with_notes,
            'notes_percentage': notes_percentage,
            'avg_notes_length': avg_notes_length
        }
