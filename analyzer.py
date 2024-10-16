import requests
import pandas as pd
from datetime import datetime, timedelta
import os

# Read Cloudflare API credentials and date range from environment variables
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID")
START_DATE = os.getenv("START_DATE")  # e.g., "2023-10-01"
END_DATE = os.getenv("END_DATE")  # e.g., "2023-10-07"

if not API_TOKEN or not ZONE_ID:
    raise ValueError("Missing API_TOKEN or ZONE_ID in environment variables.")

if not START_DATE or not END_DATE:
    raise ValueError("Missing START_DATE or END_DATE in environment variables.")

# Convert start and end dates from environment variables to datetime objects
start_date = datetime.strptime(START_DATE, "%Y-%m-%d")
end_date = datetime.strptime(END_DATE, "%Y-%m-%d")

# API endpoint for Cloudflare GraphQL Analytics
CLOUDFLARE_GRAPHQL_URL = "https://api.cloudflare.com/client/v4/graphql"

# Headers for API authentication
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def fetch_security_events_graphql(start_time, end_time):
    query = """
    query GetSecurityEvents($zoneTag: String!, $startTime: String!, $endTime: String!) {
      viewer {
        zones(filter: {zoneTag: $zoneTag}) {
          firewallEventsAdaptive(
            filter: {
              datetime_geq: $startTime,
              datetime_leq: $endTime
            }
            limit: 10000
          ) {
            action
            clientAsn
            clientCountryName
            clientIP
            clientRequestPath
            clientRequestQuery
            datetime
            source
            userAgent
          }
        }
      }
    }
    """
    
    variables = {
        "zoneTag": ZONE_ID,
        "startTime": start_time,
        "endTime": end_time
    }
    
    response = requests.post(
        CLOUDFLARE_GRAPHQL_URL,
        headers=headers,
        json={"query": query, "variables": variables}
    )
    
    if response.status_code == 200:
        return response.json()["data"]["viewer"]["zones"][0]["firewallEventsAdaptive"]
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return []

def get_events_for_date_range(start_date, end_date):
    current_date = start_date
    all_events = []

    while current_date <= end_date:
        next_day = current_date + timedelta(days=1)
        print(f"Fetching events for {current_date.strftime('%Y-%m-%d')}...")

        # Fetch events for the current day using GraphQL API
        events = fetch_security_events_graphql(
            start_time=current_date.strftime("%Y-%m-%dT00:00:00Z"),
            end_time=next_day.strftime("%Y-%m-%dT00:00:00Z")
        )

        if events:
            all_events.extend(events)

        # Move to the next day
        current_date = next_day

    return all_events

# Get events across multiple days
events = get_events_for_date_range(start_date, end_date)

# Convert the results into a DataFrame for analysis
df = pd.DataFrame(events)

# Save the logs to a CSV file
csv_filename = "cloudflare_security_events.csv"
df.to_csv(csv_filename, index=False)

# Print confirmation of file saved
print(f"All events have been saved to {csv_filename}")
