import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pyvisa as visa
import time

# Initialize the app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.H1('Keithley 2661 and 34401A Measurement App'),
    html.Div([
        html.Label('Initial Current (A):'),
        dcc.Input(id='initial-current', type='number', value=-0.001),
        html.Label('Final Current (A):'),
        dcc.Input(id='final-current', type='number', value=0.001),
        html.Label('Number of Points:'),
        dcc.Input(id='num-points', type='number', value=101),
        html.Label('Keithley GPIB Address:'),
        dcc.Input(id='keithley-gpib', type='text', value='GPIB0::12::INSTR'),
        html.Label('34401A GPIB Address:'),
        dcc.Input(id='dmm-gpib', type='text', value='GPIB0::22::INSTR'),
        html.Button('Start Measurement', id='start-measurement'),
        html.Br(),
        dcc.Graph(id='measurement-plot')
    ])
])

# Define the measurement function
def measure_current_voltage(initial_current, final_current, num_points, keithley_gpib, dmm_gpib):
    # Initialize the instruments
    rm = visa.ResourceManager()
    keithley = rm.open_resource(keithley_gpib)
    dmm = rm.open_resource(dmm_gpib)

    # Set up the Keithley for current sourcing
    keithley.write(':SENS:FUNC "CURR"')
    keithley.write(':SOUR:FUNC CURR')
    keithley.write(':SOUR:CURR:MODE FIX')
    keithley.write(':SENS:CURR:PROT 1') # Set compliance current to 1mA

    # Set up the DMM for voltage measurement
    dmm.write(':CONF:VOLT:DC')
    dmm.write(':VOLT:DC:RANG 10') # Set the voltage range to 10V

    # Define the current ramp parameters
    start_curr = initial_current
    end_curr = final_current
    num_steps = num_points
    step_size = (end_curr - start_curr) / (num_steps - 1) # Step size
    ramp_duration = 1 # Duration of each ramp (in seconds)

    # Set up the data file for recording the measurements
    data = []

    # Ramp up the current and measure the voltage at each point
    for i in range(num_steps):
        curr = start_curr + i * step_size
        keithley.write(':SOUR:CURR:LEV {:.6f}'.format(curr)) # Set the current level
        time.sleep(ramp_duration / num_steps) # Wait for the current to settle
        curr_meas = float(keithley.query(':MEAS:CURR?'))
        volt_meas = float(dmm.query(':READ?'))
        data.append((curr_meas, volt_meas))

    # Ramp down the current and measure the voltage at each point
    for i in range(num_steps):
        curr = end_curr - i * step_size
        keithley.write(':SOUR:CURR:LEV {:.6f}'.format(curr)) # Set the current level


# Define the app callback

@app.callback(
Output('measurement-plot', 'figure'),
Input('start-measurement', 'n_clicks'),
State('initial-current', 'value'),
State('final-current', 'value'),
State('num-points', 'value'),
State('keithley-gpib', 'value'),
State('dmm-gpib', 'value')
)
def update_measurement_plot(n_clicks, initial_current, final_current, num_points, keithley_gpib, dmm_gpib):
	# Only update the plot if the button has been clicked
	if n_clicks is None:
		return {}
	# Measure the current and voltage data
	data = measure_current_voltage(initial_current, final_current, num_points, keithley_gpib, dmm_gpib)

	# Extract the current and voltage arrays from the data
	current_array = [x[0] for x in data]
	voltage_array = [x[1] for x in data]

	# Create the plot
	fig = {
		'data': [{
             'x': current_array, 
             'y': voltage_array, 
             'type': 'line'
             }],
		'layout': {
             'title': 'Current vs. Voltage', 
             'xaxis': {'title': 'Current (A)'}, 
             'yaxis': {'title': 'Voltage (V)'}
             }
	}

	# Return the plot
	return fig


if __name__ == '__main__':
    app.run_server(debug=True)