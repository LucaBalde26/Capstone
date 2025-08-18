# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Dropdown options (includes "All Sites")
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())
]

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Launch Site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    html.Br(),

    # TASK 2: Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Add a slider to select payload range
    # dcc.RangeSlider(id='payload-slider',...)
    dcc.RangeSlider(
        id='payload-slider',
        min=0,                      # start (Kg)
        max=10000,                  # end (Kg)
        step=1000,                  # interval (Kg)
        value=[min_payload, max_payload],   # current selected range
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'}
    ),

    # TASK 4: Scatter chart
    html.Br(),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback for pie chart (kept here for completeness)
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        df_success = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(df_success, names='Launch Site',
                     title='Total Success Launches By Site')
    else:
        df_site = spacex_df[spacex_df['Launch Site'] == entered_site]
        counts = df_site['class'].value_counts().rename_axis('Outcome').reset_index(name='Count')
        counts['Outcome'] = counts['Outcome'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(counts, values='Count', names='Outcome',
                     title=f'Total Success vs Failure for {entered_site}')
    return fig

# TASK 4: Add a callback for payload scatter
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    # Filter by payload range first
    df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    # If-Else for ALL vs specific site
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]
        title = f'Payload vs. Success for {selected_site}'
    else:
        title = 'Payload vs. Success for All Sites'

    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',  # color-label by booster version
        title=title
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=False)
