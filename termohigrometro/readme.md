# Arduino Data Logger with Dash

This project is a Dash application that logs data from an Arduino device connected via a serial port. The application allows you to select a COM port, specify a file path to save the data in CSV format, and plot the data over time. It also includes start and stop buttons to control the data logging process.

## Project Structure

arduino-dash-app/
├── main_termohigrometro_rev1.py
├── termohigrometro_rev1.py
├── app.py
├── requirements.txt
└── data/
	└── data.csv



## Dependencies

The following libraries are required to run this project:

- dash
- dash-bootstrap-components
- pandas
- plotly
- pyserial

You can install these dependencies using the `requirements.txt` file.

```sh
pip install -r requirements.txt
```

## How to Run

1.__Ensure all dependencies are installed:__

```python
pip install -r requirements.txt
```


2.__Run the Dash application:__ Execute the [app.py](C:\Users\realm.DESKTOP-DQ0IJ8Q\Documents\Python Scripts\termohigrometro\arduino-dash-app\app.py) file to start the Dash server:

```sh
python app.py
```

3.__Access the application:__ Open your web browser and navigate to `http://localhost:8050` to access the Dash application.

4.__Using the Batch File:__ Alternatively, you can use the provided batch file to run the application:
    Create a file named `run_app.bat` with the following content:

```sh
@echo off
REM Change to the directory where your app.py is located
cd /d "C:\Users\realm.DESKTOP-DQ0IJ8Q\Documents\Python Scripts\termohigrometro\arduino-dash-app"

REM Optional: Activate your virtual environment if you are using one
REM call venv\Scripts\activate

REM Run the Dash application
python app.py

REM Pause to keep the command prompt open after the script finishes
pause
```

Double-click the `run_app.bat` file to execute it.

## How It Works
1.elect COM Port: Use the dropdown menu to select the COM port to which your Arduino is connected.

2.Specify File Path: Enter the file path where you want to save the CSV file containing the logged data.

3.Start and Stop Measuring:
*Click the "Start Measuring" button to begin logging data from the Arduino.
*Click the "Stop Measuring" button to stop logging data.

4.Plot Data: The application will plot the data in real-time on a graph.

## Contributing
Feel free to submit issues or pull requests for improvements or bug fixes.

## License
This project is licensed under the MIT License.


This `README.md` file provides an overview of the project, instructions on how to install dependencies, run the application, and a brief explanation of how the application works.
