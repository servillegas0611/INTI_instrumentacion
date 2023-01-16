# Program developed by Mariano A. Real from a base program from chatGPT
# Email: mreal@inti.gob.ar
# Date: 2023-01


import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import time
import subprocess


"""
This program creates a Dash application with a start and stop button, and a graph. When the start button is pressed, it starts a loop that calls a python script called measurement.py using the subprocess library, this script should start a measurement, save its output to a file named 'measured.csv'. Then the program reads the data from the 'measured.csv' file and plots it on the graph. The program stops when the stop button is pressed.
Please note that this is just an example, you may need to adjust it according to your specific requirements and data structure. Also, make sure you have the necessary libraries installed before running the program.
You also need to have the measurement.py script in the same directory as the Dash program file. 
"""



# import external css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# use the next lines to change the looks of the program to bootstrap
#import dash_bootstrap_components as dbc
#external_stylesheets = [dbc.themes.CERULEAN]
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H2('Measurement and plotting'),
    dcc.Graph(id='graph-with-button'),
    html.Button('Start', id='start-button', n_clicks=0),
    html.Button('Stop', id='stop-button', n_clicks=0)
])

@app.callback(
    Output('graph-with-button', 'figure'),
    [Input('start-button', 'n_clicks'),
     Input('stop-button', 'n_clicks')])
def update_figure(start_button, stop_button):
    if start_button > stop_button:
        while True:
            # uncomment the next line if you want to call the measurement program before plotting
            #subprocess.run(["python","measurement.py"])
            df = pd.read_csv('measured.csv', delimiter= ';')
            traces = []
            x_axis = 'time'
            for col in df.columns:
                traces.append(go.Scatter(x=df['x_axis'], y=df['y_axis'], mode='lines', name=col))
            figure = {'data': traces, 'layout': go.Layout(title='Measurement Data')}
            time.sleep(1)
            return figure
    else:
        return {'data': [], 'layout': go.Layout(title='Measurement Data')}


if __name__ == '__main__':
    app.run_server(debug=True)
