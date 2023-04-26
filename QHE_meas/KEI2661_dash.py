import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import visa
import time

# Initialize the instrument
rm = visa.ResourceManager()
keithley = rm.open_resource('GPIB0::12::INSTR') # Replace '12' with your Keithley's GPIB address

# Set up the Keithley for current sourcing
keithley.write(':SENS:FUNC "CURR"')
keithley.write(':SOUR:FUNC CURR')
keithley.write(':SOUR:CURR:MODE FIX')
keithley.write(':SENS:CURR:PROT 1') # Set compliance current to 1mA

# Define the current ramp parameters
start_curr = -0.001 # Starting current (-1mA)
end_curr = 0.001 # Ending current (1mA)
num_steps = 101 # Number of steps (including zero)
step_size = (end_curr - start_curr) / (num_steps - 1) # Step size
ramp_duration = 1 # Duration of each ramp (in seconds)

# Create the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div(children=[
    html.H1('Keithley 2661 Current Ramp'),
    html.Button('Start Ramp', id='start-button', n_clicks=0),
    dcc.Graph(id='current-plot', animate=True),
])

# Define the app callbacks
@app.callback(Output('current-plot', 'figure'),
              [Input('start-button', 'n_clicks')],
              [State('current-plot', 'figure')])
def start_ramp(n_clicks, figure):
    if n_clicks > 0:
        # Initialize the data trace for the plot
        data = [go.Scatter(x=[], y=[], mode='lines', name='Current (mA)')]
        
        # Set the current ramp parameters
        curr_vals = []
        times = []
        
        # Ramp up the current
        for i in range(num_steps):
            curr = start_curr + i * step_size
            keithley.write(':SOUR:CURR:LEV {:.6f}'.format(curr)) # Set the current level
            time.sleep(ramp_duration / num_steps) # Wait for the current to settle
            curr_meas = float(keithley.query(':MEAS:CURR?'))
            curr_vals.append(curr_meas)
            times.append(time.time())
            
        # Ramp down the current
        for i in range(num_steps):
            curr = end_curr - i * step_size
            keithley.write(':SOUR:CURR:LEV {:.6f}'.format(curr)) # Set the current level
            time.sleep(ramp_duration / num_steps) # Wait for the current to settle
            curr_meas = float(keithley.query(':MEAS:CURR?'))
            curr_vals.append(curr_meas)
            times.append(time.time())
        
        # Create the plot trace
        data[0]['x'] = times
        data[0]['y'] = curr_vals
        
        # Update the plot layout
        layout = go.Layout(xaxis=dict(title='Time (s)'),
                           yaxis=dict(title='Current (mA)',
                                      range=[start_curr*1000, end_curr*1000]))
        
        # Return the
		return {'data': data, 'layout': layout}

	else:
		# Return an empty plot if the button has not been clicked yet
		return {'data': [], 'layout': {}}


# RUN THE APP

if name == 'main':
app.run_server(debug=True)