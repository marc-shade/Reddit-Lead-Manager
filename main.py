import streamlit as st
import pandas as pd
from datetime import datetime
from lead_manager import LeadManager
from storage import LocalStorage
from utils import format_date, clean_text

def main():
    st.set_page_config(
        page_title="Reddit Lead Manager",
        page_icon="📊",
        layout="wide"
    )

    st.title("Reddit Lead Manager")

    # Initialize components
    storage = LocalStorage()
    lead_manager = LeadManager(storage)

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload your own CSV file",
        type=['csv'],
        help="Upload a CSV file containing leads data. Required columns: summary, lowHangingFruit, originalPost, solution, date, url, subreddit"
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        # Sync button with appropriate label
        sync_label = "🔄 Refresh from uploaded CSV" if uploaded_file else "🔄 Refresh from default CSV"
        if st.button(sync_label):
            with st.spinner("Loading data from CSV..."):
                success, error = lead_manager.sync_leads(uploaded_file)
                if success:
                    st.success("Data refresh complete!")
                else:
                    st.error(f"Failed to load data: {error}")

    # Get all leads
    leads_df = lead_manager.get_leads()
    
    if leads_df is None or leads_df.empty:
        st.info("No leads available. Click 'Refresh from CSV' to fetch leads.")
        return

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=["New", "In Progress", "Contacted", "Closed"],
            default=["New", "In Progress"]
        )
    
    with col2:
        subreddit_filter = st.multiselect(
            "Filter by Subreddit",
            options=leads_df['subreddit'].unique().tolist()
        )

    # Apply filters
    filtered_df = leads_df.copy()
    if status_filter:
        filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
    if subreddit_filter:
        filtered_df = filtered_df[filtered_df['subreddit'].isin(subreddit_filter)]

    # Initialize session state for selected leads
    if 'selected_leads' not in st.session_state:
        st.session_state.selected_leads = set()

    # Bulk Actions Section
    st.subheader("Bulk Actions")
    bulk_col1, bulk_col2 = st.columns([1, 2])
    
    with bulk_col1:
        bulk_status = st.selectbox(
            "Update Status for Selected Leads",
            options=["", "New", "In Progress", "Contacted", "Closed"],
            key="bulk_status"
        )
        if bulk_status and st.button("Apply Status Update"):
            if st.session_state.selected_leads:
                lead_manager.bulk_update_status(list(st.session_state.selected_leads), bulk_status)
                st.success(f"Updated status to '{bulk_status}' for {len(st.session_state.selected_leads)} leads")
                st.session_state.selected_leads = set()
                st.rerun()
            else:
                st.warning("Please select leads first")

    with bulk_col2:
        bulk_notes = st.text_area("Add Notes to Selected Leads")
        if bulk_notes and st.button("Add Notes"):
            if st.session_state.selected_leads:
                lead_manager.bulk_append_notes(list(st.session_state.selected_leads), bulk_notes)
                st.success(f"Added notes to {len(st.session_state.selected_leads)} leads")
                st.session_state.selected_leads = set()
                st.rerun()
            else:
                st.warning("Please select leads first")

    # Select All Checkbox
    if filtered_df.shape[0] > 0:
        if st.checkbox("Select All Visible Leads", key="select_all"):
            st.session_state.selected_leads = set(filtered_df.index)
        elif not any(st.session_state.get(f"select_{idx}", False) for idx in filtered_df.index):
            st.session_state.selected_leads = set()

    # Display leads with updated layout
    for idx, row in filtered_df.iterrows():
        # Create columns for each lead item
        check_col, lead_col = st.columns([1, 6])
        
        # Checkbox in the first (narrow) column
        with check_col:
            is_selected = st.checkbox(
                "Select Lead",  # Updated label for accessibility
                key=f"select_{idx}",
                value=idx in st.session_state.selected_leads,
                label_visibility="visible"
            )
            
            if is_selected and idx not in st.session_state.selected_leads:
                st.session_state.selected_leads.add(idx)
            elif not is_selected and idx in st.session_state.selected_leads:
                st.session_state.selected_leads.remove(idx)

        # Expander in the second (wider) column
        with lead_col:
            with st.expander(f"{row['summary'][:100]}...", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Original Post:**\n{row['originalPost']}")
                    st.markdown(f"**Solution:**\n{row['solution']}")
                    
                with col2:
                    if st.button("🔗 Open Reddit Post", key=f"url_{idx}"):
                        st.markdown(f"<script>window.open('{row['url']}', '_blank');</script>", unsafe_allow_html=True)
                    st.markdown(f"**Date:** {format_date(row['date'])}")
                    st.markdown(f"**Subreddit:** r/{row['subreddit']}")
                    
                    # Status selector
                    new_status = st.selectbox(
                        "Status",
                        options=["New", "In Progress", "Contacted", "Closed"],
                        key=f"status_{idx}",
                        index=["New", "In Progress", "Contacted", "Closed"].index(row['status'])
                    )
                    
                    if new_status != row['status']:
                        lead_manager.update_lead_status(idx, new_status)
                        st.rerun()

                    # Notes
                    notes = st.text_area(
                        "Notes",
                        value=row.get('notes', ''),
                        key=f"notes_{idx}",
                        height=100
                    )
                    
                    if notes != row.get('notes', ''):
                        lead_manager.update_lead_notes(idx, notes)

if __name__ == "__main__":
    main()
