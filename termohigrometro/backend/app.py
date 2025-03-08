import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import json
import os
import threading
import time
from datetime import datetime
from termohigrometro_rev1 import list_serial_ports, open_serial_connection, read_data
import serial.tools.list_ports

app = dash.Dash(__name__)

# Global variables to control the data acquisition thread and file name
data_acquisition_running = False
str_file = ''
selected_port = 'COM3'

def data_acquisition():
    global data_acquisition_running, str_file, selected_port
    port = selected_port
    baudrate = 115200
    v_timeout = int(1)
    arduino = open_serial_connection(port, baudrate, timeout=v_timeout)
    array_time, array_T, array_H, array_P = [], [], [], []
    str_file = 'data_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.dat'
    
    try:
        while data_acquisition_running:
            T = float(read_data(arduino, 'T?\r\n'))
            H = float(read_data(arduino, 'H?\r\n'))
            P = float(read_data(arduino, 'P?\r\n'))
            t = datetime.now()
            
            array_time.append(t)
            array_T.append(T)
            array_H.append(H)
            array_P.append(P)
            
            df = pd.DataFrame({'time': array_time, 'T': array_T, 'H': array_H, 'P': array_P})
            df.to_csv(str_file, index=False, sep='\t')
            
            latest_values = {'time': t.strftime('%Y-%m-%d %H:%M:%S'), 'T': T, 'H': H, 'P': P}
            with open('latest_values.json', 'w') as f:
                json.dump(latest_values, f)
            
            time.sleep(10)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        arduino.close()

def get_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [{'label': port.device, 'value': port.device} for port in ports]

app.layout = html.Div([
    html.H1("Termohigrómetro Dashboard"),
    dcc.Dropdown(id='com-port-dropdown', options=get_serial_ports(), placeholder='Select COM Port'),
    html.Button('Test COM Port', id='test-com-port-button', n_clicks=0),
    html.Div(id='com-port-status', children='COM Port Status: N/A'),
    dcc.Input(id='file-input', type='text', placeholder='Enter file name', value=''),
    html.Button('Start', id='start-button', n_clicks=0),
    html.Button('Stop', id='stop-button', n_clicks=0),
    html.Div(id='latest-values', children=[
        html.P("Latest Temperature: N/A", id='latest-temp'),
        html.P("Latest Humidity: N/A", id='latest-humidity'),
        html.P("Latest Pressure: N/A", id='latest-pressure')
    ]),
    dcc.Graph(id='temp-graph'),
    dcc.Graph(id='humidity-graph'),
    dcc.Graph(id='pressure-graph'),
    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0)
])

@app.callback(
    Output('com-port-status', 'children'),
    [Input('test-com-port-button', 'n_clicks')],
    [State('com-port-dropdown', 'value')]
)
def test_com_port(n_clicks, selected_port):
    if n_clicks > 0 and selected_port:
        try:
            arduino = open_serial_connection(port=selected_port, baudrate=115200, timeout=1)
            arduino.close()
            return f'COM Port Status: {selected_port} is working'
        except Exception as e:
            return f'COM Port Status: {selected_port} is not working. Error: {e}'
    return 'COM Port Status: N/A'

@app.callback(
    [Output('latest-temp', 'children'),
     Output('latest-humidity', 'children'),
     Output('latest-pressure', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_latest_values(n):
    if os.path.exists('latest_values.json'):
        with open('latest_values.json', 'r') as f:
            latest_values = json.load(f)
        return (f"Latest Temperature: {latest_values['T']} °C",
                f"Latest Humidity: {latest_values['H']} %",
                f"Latest Pressure: {latest_values['P']} hPa")
    return ("Latest Temperature: N/A", "Latest Humidity: N/A", "Latest Pressure: N/A")

@app.callback(
    [Output('temp-graph', 'figure'),
     Output('humidity-graph', 'figure'),
     Output('pressure-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    global str_file
    if str_file and os.path.exists(str_file):
        df = pd.read_csv(str_file, sep='\t', parse_dates=['time'])
        temp_fig = go.Figure([go.Scatter(x=df['time'], y=df['T'], mode='lines', name='Temperature')])
        humidity_fig = go.Figure([go.Scatter(x=df['time'], y=df['H'], mode='lines', name='Humidity')])
        pressure_fig = go.Figure([go.Scatter(x=df['time'], y=df['P'], mode='lines', name='Pressure')])
        
        temp_fig.update_layout(xaxis_title='Time', yaxis_title='Temperature (°C)', autosize=True)
        humidity_fig.update_layout(xaxis_title='Time', yaxis_title='Humidity (%)', autosize=True)
        pressure_fig.update_layout(xaxis_title='Time', yaxis_title='Pressure (hPa)', autosize=True)
        
        return temp_fig, humidity_fig, pressure_fig
    return {}, {}, {}

@app.callback(
    Output('interval-component', 'disabled'),
    [Input('start-button', 'n_clicks'),
     Input('stop-button', 'n_clicks')],
    [State('com-port-dropdown', 'value')]
)
def control_data_acquisition(start_clicks, stop_clicks, selected_port_value):
    global data_acquisition_running, selected_port
    ctx = dash.callback_context

    if not ctx.triggered:
        return False
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'start-button':
        if not data_acquisition_running:
            selected_port = selected_port_value
            data_acquisition_running = True
            threading.Thread(target=data_acquisition).start()
        return False
    elif button_id == 'stop-button':
        data_acquisition_running = False
        return True

if __name__ == '__main__':
    app.run_server(debug=True)