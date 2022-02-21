# Import required libraries
import pandas as pd
import dash
from dash import html, dcc                     # dcc = Dash Core Components
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
print('Max', max_payload, 'Min', min_payload)
marks = range(0, 10001, 2500)
markDict = {}
for mark in marks:
    markDict[mark] = str(mark)

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                    options = [{'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'Cape Canaveral Launch Site 40', 'value': 'CCAFS LC-40'},
                                        {'label': 'Vandenberg Space Launch Complex 4E', 'value': 'VAFB SLC-4E'}, 
                                        {'label': 'Kennedy Launch Complex 39A', 'value': 'KSC LC-39A'},
                                        {'label': 'Cape Canaveral Space Launch Complex 40', 'value': 'CCAFS SLC-40'}], 
                                    value='ALL', placeholder='Select Launch Site', searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                # markDict was calculated above, before we got into app.layout
                                dcc.RangeSlider(id='payload-slider',min=0, max=10000, step=1000, marks=markDict,
                                    value=(min_payload, max_payload)
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# this decorator makes the framework automatically call this function when the Input changes, and
#    set the 'figure' attribute of the Output to the output of this function
@app.callback( Output('success-pie-chart', 'figure'), Input('site-dropdown', 'value'))
def site_changed(launchSite):                 # launchSite will be one of 'ALL', 'CCAFS LC40', etc.
    if (launchSite == 'ALL'):
        filtered_df = spacex_df[spacex_df['class']==1].groupby('Launch Site')['class'].value_counts()
        launchSiteList = [stuff[0] for stuff in filtered_df.index]
        fig = px.pie(filtered_df, values='class', names=launchSiteList, title='Successes by Launch Site')

    else:
        filtered_df = spacex_df[spacex_df['Launch Site']==launchSite]['class'].value_counts()
        fig = px.pie(filtered_df, values='class', names={0: 'failure', 1: 'success'}, title='Success Rate for '+launchSite)
    return(fig)

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback( Output('success-payload-scatter-chart', 'figure'), 
                [Input('site-dropdown', 'value'), Input('payload-slider', 'value')]
)
def site_or_payload_changed(launchSite, payloadRange):
    [payloadRangeMin, payloadRangeMax] = payloadRange          # the value of a range slider is a list of length 2
    dfTmp = spacex_df[spacex_df['Payload Mass (kg)'] >= payloadRangeMin]
    dfTmp = dfTmp[dfTmp['Payload Mass (kg)'] <= payloadRangeMax]
    if (launchSite != 'ALL'):
        dfTmp = dfTmp[dfTmp['Launch Site'] == launchSite]
    fig = px.scatter(dfTmp, x='Payload Mass (kg)', y='class', color='Booster Version Category')
    return(fig)

# Run the app
if __name__ == '__main__':
    app.run_server()
