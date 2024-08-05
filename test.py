import requests
import calendar
from io import BytesIO
import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

def get_file_url(base_url, year, month):
    """Constructs the URL for a given year and month."""
    month_name = calendar.month_name[month].lower()
    file_url = f"{base_url}/{month_name}_generator{year}.xlsx"
    return file_url

def file_exists(url):
    """Checks if the file at the given URL exists."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'excel' in content_type or 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type:
                return True
        return False
    except requests.exceptions.RequestException:
        return False

def get_latest_file_url(base_url):
    """Finds the latest file URL."""
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    while True:
        file_url = get_file_url(base_url, current_year, current_month)
        
        if file_exists(file_url):
            return file_url, current_year, current_month
        
        # Move to the previous month
        if current_month == 1:
            current_month = 12
            current_year -= 1
        else:
            current_month -= 1
            
        # Stop if going back more than 12 months
        if current_year < now.year - 1:
            st.error("No recent file found within the last year.")
            return None, None, None

def get_previous_file_url(base_url, year, month):
    """Constructs the URL for the previous month's file."""
    if month == 1:
        month = 12
        year -= 1
    else:
        month -= 1
    month_name = calendar.month_name[month].lower()
    return f"https://www.eia.gov/electricity/data/eia860m/archive/xls/{month_name}_generator{year}.xlsx"

def download_excel_file(url):
    """Downloads the Excel file from the given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors
        
        content_type = response.headers.get('Content-Type', '')
        if 'excel' in content_type or 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type:
            return BytesIO(response.content)
        else:
            st.error("Downloaded file is not an Excel file.")
            return None
    except requests.exceptions.RequestException as err:
        st.error(f"Request Exception occurred: {err}")
        return None

def rename_columns(df):
    """Renames columns to 'Nameplate Capacity (MW)' if it is unnamed and located in column index 12."""
    if df.columns[12] == 'Unnamed: 12':
        df.rename(columns={df.columns[12]: 'Nameplate Capacity (MW)'}, inplace=True)
    if df.columns[15] == 'Unnamed: 15':
        df.rename(columns={df.columns[15]: 'Technology'}, inplace=True)
    return df 

def sum_nameplate_capacity(df):
    """Sums up the 'Nameplate Capacity (MW)' column from the given DataFrame, starting from row 2, converting non-numeric values to NaN."""
    df = rename_columns(df)  # Ensure columns are correctly named
    if 'Nameplate Capacity (MW)' in df.columns:
        df['Nameplate Capacity (MW)'] = pd.to_numeric(df['Nameplate Capacity (MW)'], errors='coerce')  # Convert to numeric, setting errors to NaN
        
        # Slice the DataFrame to start from row 2
        df_to_sum = df.iloc[1:]
        
        return df_to_sum['Nameplate Capacity (MW)'].sum()  # Sum up the column starting from row 2
    else:
        st.warning("'Nameplate Capacity (MW)' column not found.")
        return 0

def count_plants(df):
    """Counts the number of plants in the given DataFrame."""
    return df.shape[0]

def plot_comparison(latest_sums, previous_sums, capacity_type):
    """Plots a bar graph comparing capacities of the latest and previous months for a specific type."""
    df_comparison = pd.DataFrame({
        'Sheet': latest_sums.keys(),
        'Latest Month': latest_sums.values(),
        'Previous Month': previous_sums.values()
    })

    fig, ax = plt.subplots()
    df_comparison.plot(x='Sheet', kind='bar', ax=ax)
    plt.title(f'Comparison of {capacity_type} Capacity (MW)')
    plt.ylabel('Total Nameplate Capacity (MW)')
    
    # Adjust axis formatting to avoid scientific notation
    ax.ticklabel_format(style='plain', axis='y')
    
    # Calculate the min and max values for setting y-axis limits
    all_values = list(latest_sums.values()) + list(previous_sums.values())
    min_value = min(all_values, default=0)
    max_value = max(all_values, default=0)
    
    # Set y-axis limits
    ax.set_ylim(min_value-200, 200+ max_value)
    
    # Calculate the change and display it
    changes = {sheet: latest_sums.get(sheet, 0) - previous_sums.get(sheet, 0) for sheet in latest_sums}
    
    st.pyplot(fig)
    
    st.write(f"Change in {capacity_type} Capacity (MW):")
    for sheet, change in changes.items():
        st.write(f"{int(change)} MW. {int(latest_sums.get(sheet,0))} MW in latest month, {int(previous_sums.get(sheet, 0))} MW in previous month.")


def plot_plant_comparison(latest_counts, previous_counts, capacity_type):
    """Plots a bar graph comparing the number of plants for the latest and previous months for a specific type."""
    df_comparison = pd.DataFrame({
        'Sheet': latest_counts.keys(),
        'Latest Month': latest_counts.values(),
        'Previous Month': previous_counts.values()
    })

    fig, ax = plt.subplots()
    df_comparison.plot(x='Sheet', kind='bar', ax=ax)
    plt.title(f'Comparison of Number of {capacity_type} Plants')
    plt.ylabel('Number of Plants')
    
    # Adjust axis formatting to avoid scientific notation
    ax.ticklabel_format(style='plain', axis='y')
    
    # Calculate the min and max values for setting y-axis limits
    all_values = list(latest_counts.values()) + list(previous_counts.values())
    min_value = min(all_values, default=0)
    max_value = max(all_values, default=0)
    
    # Set y-axis limits
    ax.set_ylim(min_value-200, 200+ max_value)
    
    # Calculate the change and display it
    changes = {sheet: latest_counts.get(sheet, 0) - previous_counts.get(sheet, 0) for sheet in latest_counts}
    
    st.pyplot(fig)
    
    st.write(f"Change in number of {capacity_type} plants:")
    for sheet, change in changes.items():
        st.write(f"{sheet}: {change} plants. {latest_counts.get(sheet,0)} plants in latest month, {previous_counts.get(sheet, 0)} plants in previous month.")


def plot_technology_pie_charts(df_latest, df_previous, capacity_type):
    """Plots pie charts comparing the Technology used for a specific capacity type between latest and previous months."""
    df_latest = rename_columns(df_latest)
    df_previous = rename_columns(df_previous)
    
    if 'Technology' in df_latest.columns:
        # Count occurrences of each technology type
        latest_tech_counts = df_latest['Technology'].value_counts()
        previous_tech_counts = df_previous['Technology'].value_counts()

        # Combine all technologies for calculation
        all_tech_counts = pd.concat([latest_tech_counts, previous_tech_counts], axis=0)
        total_count = all_tech_counts.sum()

        # Function to create 'Other' category
        def create_other_category(tech_counts):
            tech_counts = tech_counts.copy()
            # Calculate percentages
            percentages = tech_counts / total_count * 100
            # Identify technologies to merge into 'Other'
            other_techs = percentages[percentages < 2].index
            # Create 'Other' category
            tech_counts.loc['Other'] = tech_counts[other_techs].sum()
            # Drop original small technologies
            tech_counts = tech_counts.drop(other_techs)
            return tech_counts
        
        latest_tech_counts = create_other_category(latest_tech_counts)
        previous_tech_counts = create_other_category(previous_tech_counts)

        fig, axs = plt.subplots(1, 2, figsize=(14, 7), subplot_kw=dict(aspect='equal'))
        
        # Plot latest month pie chart
        axs[0].pie(latest_tech_counts, labels=latest_tech_counts.index, autopct='%1.1f%%', startangle=140)
        axs[0].set_title(f'{capacity_type} - Latest Month Technology Distribution')
        
        # Plot previous month pie chart
        axs[1].pie(previous_tech_counts, labels=previous_tech_counts.index, autopct='%1.1f%%', startangle=140)
        axs[1].set_title(f'{capacity_type} - Previous Month Technology Distribution')
        plt.subplots_adjust(wspace=1)  # Adjust the width space between the two subplots

        st.pyplot(fig)
    else:
        st.warning("'Technology' column not found in one or both of the dataframes.")


def main():
    st.title("EIA Data Downloader and Analysis")

    base_url = "https://www.eia.gov/electricity/data/eia860m/xls"

    if st.button("Download and Process Data"):
        st.write("Finding the latest Excel file...")
        latest_file_url, latest_year, latest_month = get_latest_file_url(base_url)
        
        if latest_file_url:
            st.write(f"Downloading latest Excel file from {latest_file_url}...")
            latest_excel_data = download_excel_file(latest_file_url)
            
            if latest_excel_data is not None:
                st.write("Reading latest Excel file...")
                
                try:
                    df_dict_latest = pd.read_excel(latest_excel_data, sheet_name=None, engine='openpyxl')
                    
                    sheet_names_latest = list(df_dict_latest.keys())
                    ##st.write("Sheets found in the latest Excel file:")
                    ##st.write(sheet_names_latest)

                    tab_selection_latest = st.tabs(sheet_names_latest)

                    latest_sums = {}
                    latest_counts = {}
                    for sheet_name, tab in zip(sheet_names_latest, tab_selection_latest):
                        with tab:
                            st.write(f"Data from sheet: {sheet_name}")
                            df = df_dict_latest[sheet_name]
                            df = rename_columns(df)  # Ensure column renaming
                            st.write(df)
                            st.download_button(
                                label="Download selected sheet as CSV",
                                data=df.to_csv(index=False).encode('utf-8'),
                                file_name=f"{sheet_name}_latest.csv",
                                mime='text/csv'
                            )
                            
                            # Sum up Nameplate Capacity and count plants for the latest month
                            latest_sums[sheet_name] = sum_nameplate_capacity(df)
                            latest_counts[sheet_name] = count_plants(df)
                    
                    st.write("Finding the previous month's Excel file...")
                    previous_file_url = get_previous_file_url(base_url, latest_year, latest_month)
                    
                    if previous_file_url:
                        st.write(f"Downloading previous month's Excel file from {previous_file_url}...")
                        previous_excel_data = download_excel_file(previous_file_url)
                        
                        if previous_excel_data is not None:
                            st.write("Reading previous month's Excel file...")
                            
                            try:
                                df_dict_previous = pd.read_excel(previous_excel_data, sheet_name=None, engine='openpyxl')
                                
                                sheet_names_previous = list(df_dict_previous.keys())
                                ##st.write("Sheets found in the previous month's Excel file:")
                                ##st.write(sheet_names_previous)

                                previous_sums = {}
                                previous_counts = {}
                                for sheet_name in sheet_names_latest:
                                    if sheet_name in sheet_names_previous:
                                        df = df_dict_previous[sheet_name]
                                        df = rename_columns(df)  # Ensure column renaming
                                        previous_sums[sheet_name] = sum_nameplate_capacity(df)
                                        previous_counts[sheet_name] = count_plants(df)
                                    else:
                                        st.warning(f"Sheet {sheet_name} not found in previous month's data.")
                                        previous_sums[sheet_name] = 0
                                        previous_counts[sheet_name] = 0

                                # Plot comparisons for each type
                                for capacity_type in ['Operating', 'Planned', 'Retired']:
                                    st.write(f"Comparing {capacity_type} capacities:")
                                    plot_comparison(
                                        {sheet: latest_sums.get(sheet, 0) for sheet in [capacity_type]},
                                        {sheet: previous_sums.get(sheet, 0) for sheet in [capacity_type]},
                                        capacity_type
                                    )
                                    st.write(f"Comparing number of {capacity_type} plants:")
                                    plot_plant_comparison(
                                        {sheet: latest_counts.get(sheet, 0) for sheet in [capacity_type]},
                                        {sheet: previous_counts.get(sheet, 0) for sheet in [capacity_type]},
                                        capacity_type
                                    )
                                    
                                    # Plot technology pie charts
                                    if capacity_type in sheet_names_latest and capacity_type in sheet_names_previous:
                                        st.write(f"Technology distribution for {capacity_type}:")
                                        plot_technology_pie_charts(
                                            df_dict_latest[capacity_type],
                                            df_dict_previous[capacity_type],
                                            capacity_type
                                        )

                            except ValueError as e:
                                st.error(f"Error reading previous month's Excel file: {e}")
                        else:
                            st.error("Failed to download the previous month's Excel file.")
                    else:
                        st.error("Failed to find the previous month's Excel file.")
                except ValueError as e:
                    st.error(f"Error reading latest Excel file: {e}")
            else:
                st.error("Failed to download the latest Excel file.")
        else:
            st.error("Failed to find the latest Excel file.")

if __name__ == "__main__":
    main()
