import streamlit as st

import requests

import json

import os

import pandas as pd

import time

from datetime import datetime

import matplotlib.pyplot as plt

import calendar




# Function to fetch and process data

def fetch_and_process_data():

    global df,df2

    

    api_url = "https://api.eia.gov/v2/electricity/operating-generator-capacity/data/"

    api_key = "dOmFaNeWhnV7kyU3Bqrc0y2ot3NeqhHVsuWEDbsG"

    

    now = datetime.now()

    current_year = now.year

    current_month = now.month




    def get_headers(start_date):

        return {

            "X-Params": json.dumps({

                "frequency": "monthly",

                "data": [

                    "county",

                    "latitude",

                    "longitude",

                    "nameplate-capacity-mw",

                    "net-summer-capacity-mw",

                    "net-winter-capacity-mw",

                    "operating-year-month",

                    "planned-derate-summer-cap-mw",

                    "planned-derate-year-month",

                    "planned-retirement-year-month",

                    "planned-uprate-summer-cap-mw",

                    "planned-uprate-year-month"

                ],

                "facets": {"sector": [
                "electric-utility"
                ]},

                "start": start_date,

                "end": None,

                "sort": [

                    {

                        "column": "period",

                        "direction": "desc"

                    }

                ],

                "offset": 0,

                "length": 5000

            }),

            "Content-Type": "application/json"

        }




    # Find the most recent month with available data

    while True:

        start_date = f"{current_year}-{current_month:02d}"

        headers = get_headers(start_date)

        

        try:

            response = requests.get(api_url, params={"api_key": api_key}, headers=headers)

            if response.status_code == 403:

                st.error(f"HTTP Error 403: Forbidden. Check your API key or request headers for start date: {start_date}")

                return

            response.raise_for_status()

            data = response.json()

            

            if data['response']['data']:

                break

            else:

                current_month -= 1

                if current_month == 0:

                    current_month = 12

                    current_year -= 1




        except requests.exceptions.HTTPError as err:

            st.error(f"HTTP Error occurred: {err}")

            return

        except requests.exceptions.RequestException as err:

            st.error(f"Request Exception occurred: {err}")

            return




    all_data = []

    offset = 0

    length = 5000

    batch_number = 1




    start_time = time.time()




    while True:

        headers = get_headers(start_date)

        headers["X-Params"] = json.dumps({

            "frequency": "monthly",

            "data": [

                "county",

                "latitude",

                "longitude",

                "nameplate-capacity-mw",

                "net-summer-capacity-mw",

                "net-winter-capacity-mw",

                "operating-year-month",

                "planned-derate-summer-cap-mw",

                "planned-derate-year-month",

                "planned-retirement-year-month",

                "planned-uprate-summer-cap-mw",

                "planned-uprate-year-month"

            ],

            "facets": {"sector": [
            "electric-utility"
        ]},

            "start": start_date,

            "end": None,

            "sort": [

                {

                    "column": "period",

                    "direction": "desc"

                }

            ],

            "offset": offset,

            "length": length

        })




        try:

            response = requests.get(api_url, params={"api_key": api_key}, headers=headers)

            response.raise_for_status()

            data = response.json()

            

            if not data['response']['data']:

                st.write("No more data to retrieve.")

                break

            

            all_data.extend(data['response']['data'])

            offset += length




            st.write(f"Batch {batch_number}: Retrieved {len(data['response']['data'])} records. Total so far: {len(all_data)} records.")

            batch_number += 1




            time.sleep(1)




        except requests.exceptions.HTTPError as err:

            st.error(f"HTTP Error occurred: {err}")

            return

        except requests.exceptions.RequestException as err:

            st.error(f"Request Exception occurred: {err}")

            return




    end_time = time.time()

    elapsed_time = end_time - start_time

    st.write(f"Total records retrieved: {len(all_data)}")

    st.write(f"Total time taken: {elapsed_time:.2f} seconds")




    df = pd.DataFrame(all_data)

    if 'nameplate-capacity-mw' in df.columns:

        df["nameplate-capacity-mw"] = pd.to_numeric(df["nameplate-capacity-mw"])

    else:

        st.write("The 'nameplate-capacity-mw' column is not present in the data.")

    excel_filename = f'EIA_860_data_{start_date}.xlsx'




    df = df.rename(columns={'Plant Name':'Plant Name', 'stateName':'State','technology':'Technology','net-summer-capacity-mw':'Summer Capacity (MW)','county':'County'})




    ##df.to_excel(excel_filename, index=False)




    st.write(f"Data exported to {excel_filename}")

    ##with open(excel_filename, "rb") as file:
        ##.download_button(label="Download Current Month Data", data=file, file_name=excel_filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")



    ### previous month!!




    if current_month == 1:

        current_month = 12

    else:

        current_month -= 1




    start_date = f"{current_year}-{current_month:02d}"

    headers = get_headers(start_date)




    response = requests.get(api_url, params={"api_key": api_key}, headers=headers)

    if response.status_code == 403:

        st.error(f"HTTP Error 403: Forbidden. Check your API key or request headers for start date: {start_date}")

    response.raise_for_status()

    data2 = response.json()

        

    if 'data' not in locals() or not data2['response']['data']:

        st.write("No data available. Exiting.")

    else:

        all_data2 = []

        offset = 0

        length = 5000

        batch_number = 1




        start_time = time.time()




        while True:

            headers = get_headers(start_date)

            headers["X-Params"] = json.dumps({

                "frequency": "monthly",

                "data": [

                    "county",

                    "latitude",

                    "longitude",

                    "nameplate-capacity-mw",

                    "net-summer-capacity-mw",

                    "net-winter-capacity-mw",

                    "operating-year-month",

                    "planned-derate-summer-cap-mw",

                    "planned-derate-year-month",

                    "planned-retirement-year-month",

                    "planned-uprate-summer-cap-mw",

                    "planned-uprate-year-month"

                ],

                "facets": {"sector": [
            "electric-utility"
        ]},

                "start": start_date,

                "end": None,

                "sort": [

                    {

                        "column": "period",

                        "direction": "desc"

                    }

                ],

                "offset": offset,

                "length": length

            })




            try:

                response = requests.get(api_url, params={"api_key": api_key}, headers=headers)

                response.raise_for_status()

                data2 = response.json()

                

                if not data2['response']['data']:

                    st.write("No more data to retrieve.")

                    break

                

                all_data2.extend(data2['response']['data'])

                offset += length




                st.write(f"Batch {batch_number}: Retrieved {len(data2['response']['data'])} records. Total so far: {len(all_data2)} records.")

                batch_number += 1




                time.sleep(1)




            except requests.exceptions.HTTPError as err:

                st.error(f"HTTP Error occurred: {err}")

                break

            except requests.exceptions.RequestException as err:

                st.error(f"Request Exception occurred: {err}")

                break




        end_time = time.time()

        elapsed_time = end_time - start_time

        st.write(f"Total records retrieved: {len(all_data2)}")

        st.write(f"Total time taken: {elapsed_time:.2f} seconds")




        df2 = pd.DataFrame(all_data2)

        rows_to_keep = [index for index, row in df2.iterrows() if row['period'] == start_date]




        df2 = df2.loc[rows_to_keep]




        if 'nameplate-capacity-mw' in df.columns:

            df2["nameplate-capacity-mw"] = pd.to_numeric(df2["nameplate-capacity-mw"])

        else:

            st.write("The 'nameplate-capacity-mw' column is not present in the data.")

        excel_filename = f'EIA_860_data_{start_date}.xlsx'




        df2 = df2.rename(columns={'Plant Name':'Plant Name', 'stateName':'State','technology':'Technology','net-summer-capacity-mw':'Summer Capacity (MW)','county':'County'})




        ##df2.to_excel(excel_filename, index=False)




        st.write(f"Data exported to {excel_filename}")
        ##with open(excel_filename, "rb") as file:
            ##st.download_button(label="Download Previous Month Data", data=file, file_name=excel_filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")



        current_capacity = df["nameplate-capacity-mw"].sum()
        st.write("Current capacity: ", current_capacity)

        previous_capacity = df2["nameplate-capacity-mw"].sum()
        st.write("Previous month's capacity: ", previous_capacity)

        st.write(f"Percent change: {(current_capacity-previous_capacity)/100}")

        comparisondata = {

            "capacities": [current_capacity, previous_capacity],

            "months": [calendar.month_name[current_month+1], calendar.month_name[current_month]]

        }




        visualization = pd.DataFrame(comparisondata)




        ax = visualization.plot(kind='bar', x='months', y='capacities', legend=False)

        plt.xlabel('Month')

        plt.ylabel('Capacities')

        plt.title('Current Month vs Previous Month EIA Listed Capacities')




        plt.savefig('EIA_graph.png')




        visualization.to_excel("visualization.xlsx", index=False)

        st.write("Visualization exported.")

        st.image('EIA_graph.png')








def compare_fuel_types(df, df2):

    
    df.rename(columns={
        'plantName': 'Plant Name',
        'stateName': 'State',
        'technology': 'Technology',
        'net-summer-capacity-mw': 'Summer Capacity (MW)',
        'county': 'County'
    }, inplace=True)
    
    df2.rename(columns={
            'plantName': 'Plant Name',
            'stateName': 'State',
            'technology': 'Technology',
            'net-summer-capacity-mw': 'Summer Capacity (MW)',
            'county': 'County'
        }, inplace=True)
    
    # Debugging: Print dataframes before any processing
    st.write("DataFrame df before processing:")
    st.write(df)
    st.write("DataFrame df2 before processing:")
    st.write(df2)
    
    # Identify unique facilities
    unique_current = df[['Plant Name']].drop_duplicates()
    unique_previous = df2[['Plant Name']].drop_duplicates()
    
    unique_to_current = unique_current[~unique_current['Plant Name'].isin(unique_previous['Plant Name'])]
    unique_to_previous = unique_previous[~unique_previous['Plant Name'].isin(unique_current['Plant Name'])]
    
    # Debugging: Print unique dataframes
    st.write("Unique current plants:")
    st.write(unique_current)
    st.write("Unique previous plants:")
    st.write(unique_previous)
    st.write("Unique to current plants:")
    st.write(unique_to_current)
    st.write("Unique to previous plants:")
    st.write(unique_to_previous)
    
    # Load fuel type data
    df_fuel = df[['Plant Name', 'energy-source-desc']]
    df2_fuel = df2[['Plant Name', 'energy-source-desc']]
    
    current_fuel_types = df_fuel[df_fuel['Plant Name'].isin(unique_to_current['Plant Name'])]
    previous_fuel_types = df2_fuel[df2_fuel['Plant Name'].isin(unique_to_previous['Plant Name'])]
    
    # Debugging: Print fuel types
    st.write("Current fuel types for unique plants:")
    st.write(current_fuel_types)
    st.write("Previous fuel types for unique plants:")
    st.write(previous_fuel_types)
    
    def percent_func(pct):
        return '' if pct < 2 else f'{pct:.1f}%'
    
    # Count fuel types
    current_fuel_counts = current_fuel_types['energy-source-desc'].value_counts()
    
    
    total_plants = current_fuel_counts.sum()

    # Create a new Series for the updated fuel type counts
    updated_fuel_counts = pd.Series()

    # Identify labels that make up less than 1% of total plants
    threshold = total_plants * 0.01

    for label in current_fuel_counts.index:
        if current_fuel_counts[label] < threshold:
            # Add to "Others" category
            if 'Others' in updated_fuel_counts:
                updated_fuel_counts['Others'] += current_fuel_counts[label]
            else:
                updated_fuel_counts['Others'] = current_fuel_counts[label]
        else:
            # Keep the label in the updated fuel counts
            updated_fuel_counts[label] = current_fuel_counts[label]
    
    labels = updated_fuel_counts.index

    previous_fuel_counts = previous_fuel_types['energy-source-desc'].value_counts()
    
    st.write(f"Number of plants in the current dataset that are not in the previous dataset: {unique_to_current.shape[0]}")
    st.write(f"Number of plants in the previous dataset that are not in the current dataset: {unique_to_previous.shape[0]}")
    
    # Plot pie charts
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    ax.pie(
        updated_fuel_counts,                     # Data for the pie chart
        labels=[label if pct >= 2 else '' for label, pct in zip(labels, current_fuel_counts)],  # Conditional labels
        autopct=percent_func,                    # Formatting percentages
        startangle=140                           # Rotation angle
    )
    
    ax.set_title('Fuel Types in Current Month')
    
    plt.show()
    
    st.pyplot(fig)


# Main Streamlit app function

def main():

    st.title("EIA Current to Previous Month Capacity Comparison")




    if st.button("Go to Data Dashboard"):

        st.write("Processing data...")

        fetch_and_process_data()

        compare_fuel_types(df, df2)




if __name__ == "__main__":

    main()