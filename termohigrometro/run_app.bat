@echo off
REM Change to the directory where your app.py is located
cd /d "C:\Users\realm.DESKTOP-DQ0IJ8Q\Documents\Python Scripts\termohigrometro\arduino-dash-app"

REM Optional: Activate your virtual environment if you are using one
REM call venv\Scripts\activate

REM Run the Dash application
python app.py

REM Pause to keep the command prompt open after the script finishes
pause