import pandas as pd
import numpy as np
from datetime import datetime
from storage import LocalStorage
from utils import clean_text

class LeadManager:
    def __init__(self, storage: LocalStorage):
        self.storage = storage
        self._leads_df = None
        self.load_leads()

    def load_leads(self):
        """Load leads from local storage"""
        self._leads_df = self.storage.load_progress()
        if self._leads_df is None:
            self._leads_df = pd.DataFrame(columns=[
                'summary', 'lowHangingFruit', 'originalPost', 'solution',
                'date', 'url', 'subreddit', 'status', 'notes'
            ])

    def sync_leads(self, uploaded_file=None):
        """Sync leads with CSV file and merge with local progress"""
        try:
            # Read from uploaded file if provided, otherwise use default CSV
            if uploaded_file is not None:
                new_leads = pd.read_csv(uploaded_file)
            else:
                new_leads = pd.read_csv("[SALES] Reddit Leads - incomingData.csv")
            
            # Validate required columns
            required_columns = ['summary', 'lowHangingFruit', 'originalPost', 'solution', 
                              'date', 'url', 'subreddit']
            missing_columns = [col for col in required_columns if col not in new_leads.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Clean text fields
            text_columns = ['summary', 'lowHangingFruit', 'originalPost', 'solution']
            for col in text_columns:
                new_leads[col] = new_leads[col].apply(clean_text)

            # Add status column if not exists
            if 'status' not in new_leads.columns:
                new_leads['status'] = 'New'
            
            # Add notes column if not exists and initialize with empty strings
            if 'notes' not in new_leads.columns:
                new_leads['notes'] = ''
            new_leads['notes'] = new_leads['notes'].fillna('').astype(str)

            # Merge with existing leads, keeping local status and notes
            if self._leads_df is not None and not self._leads_df.empty:
                # Create a mapping of existing lead status and notes
                existing_status = pd.Series(
                    self._leads_df.status.values,
                    index=self._leads_df.url
                ).to_dict()
                
                existing_notes = pd.Series(
                    self._leads_df.notes.fillna('').astype(str).values,
                    index=self._leads_df.url
                ).to_dict()

                # Update status and notes for existing leads
                new_leads.loc[new_leads.url.isin(existing_status.keys()), 'status'] = \
                    new_leads.url.map(existing_status)
                new_leads.loc[new_leads.url.isin(existing_notes.keys()), 'notes'] = \
                    new_leads.url.map(existing_notes)

            self._leads_df = new_leads
            self.storage.save_progress(self._leads_df)
            return True, None
            
        except ValueError as ve:
            return False, str(ve)
        except Exception as e:
            return False, f"Error processing CSV file: {str(e)}"

    def get_leads(self):
        """Get all leads"""
        return self._leads_df

    def update_lead_status(self, idx: int, status: str):
        """Update lead status"""
        self._leads_df.at[idx, 'status'] = status
        self.storage.save_progress(self._leads_df)

    def update_lead_notes(self, idx: int, notes: str):
        """Update lead notes"""
        # Convert any input to string, handling NaN and None values
        notes_value = '' if pd.isna(notes) or notes is None else str(notes).strip()
        
        # Ensure notes column is string type
        if not pd.api.types.is_string_dtype(self._leads_df['notes']):
            self._leads_df['notes'] = self._leads_df['notes'].fillna('').astype(str)
        
        # Update the value
        self._leads_df.at[idx, 'notes'] = notes_value
        self.storage.save_progress(self._leads_df)

    def bulk_update_status(self, indices: list, status: str):
        """Update status for multiple leads"""
        for idx in indices:
            self._leads_df.at[idx, 'status'] = status
        self.storage.save_progress(self._leads_df)

    def bulk_append_notes(self, indices: list, notes: str):
        """Append notes to multiple leads"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        formatted_note = f"\n[{timestamp}] {notes}"
        
        for idx in indices:
            current_notes = self._leads_df.at[idx, 'notes']
            current_notes = '' if pd.isna(current_notes) else str(current_notes)
            self._leads_df.at[idx, 'notes'] = current_notes + formatted_note
            
        self.storage.save_progress(self._leads_df)
