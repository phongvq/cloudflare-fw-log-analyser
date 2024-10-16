import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import StringIO
import argparse

# Set up argument parsing
parser = argparse.ArgumentParser(description='Draw a graph based on the log data.')
parser.add_argument('--group-by', type=str, default='clientIP', help='Field to group by (e.g., clientIP, clientAsn, clientCountryName)')
args = parser.parse_args()

# Read input from stdin
input_data = sys.stdin.read()

# Define column names based on your log file structure
columns = ['action', 'clientAsn', 'clientCountryName', 'clientIP', 'clientRequestPath', 
           'clientRequestQuery', 'datetime', 'source', 'userAgent']

# Parse the input data into a DataFrame
data = StringIO(input_data)
df = pd.read_csv(data, header=0, names=columns)

# Convert datetime to pandas datetime
df['datetime'] = pd.to_datetime(df['datetime'])

# Group by the chosen field and datetime
group_by_field = args.group_by
requests_per_group = df.groupby([group_by_field, 'datetime']).size().reset_index(name='requests')

# Compute total requests per group (for the bar chart)
total_requests_per_group = df.groupby(group_by_field).size().reset_index(name='total_requests')

# Create a subplot with two plots: the line plot on the left, and the total requests bar chart on the right
fig = make_subplots(
    rows=1, cols=2, 
    column_widths=[0.7, 0.3],  # Adjust the width of the two plots
    subplot_titles=[f'Requests by {group_by_field} Over Time', f'Total Requests by {group_by_field}'],
    shared_yaxes=True
)

# Line plot for requests over time
for group_value in requests_per_group[group_by_field].unique():
    group_df = requests_per_group[requests_per_group[group_by_field] == group_value]
    fig.add_trace(
        go.Scatter(x=group_df['datetime'], y=group_df['requests'], mode='lines+markers', name=str(group_value)),
        row=1, col=1
    )

# Bar chart for total requests per group
fig.add_trace(
    go.Bar(x=total_requests_per_group['total_requests'], y=total_requests_per_group[group_by_field], 
           orientation='h', name='Total Requests', marker=dict(color='rgba(58, 71, 80, 0.6)', line=dict(color='rgba(58, 71, 80, 1.0)', width=2))),
    row=1, col=2
)

# Update layout for better visualization
fig.update_layout(
    title_text=f'Number of Requests by {group_by_field}',
    xaxis_title='Time',
    yaxis_title='Number of Requests',
    xaxis2_title='Total Requests',
    yaxis2=dict(showticklabels=False),  # Hide tick labels on the right y-axis
    height=600,  # Set a height for the graph
    showlegend=False  # Hide legend (can be adjusted to show it if desired)
)

# Show the interactive plot
fig.show()

