# INTI instrumentation

Some programs developed to be used at INTI to measure things.


## QHE meas

Folder: \QHE_meas

Here we include some programs based on [Dash](see https://plotly.com/dash/?utm_source=google&utm_medium=cpc&gclid=CjwKCAjwl6OiBhA2EiwAuUwWZXYuciV8XUVqvwWFY9kpnKXTXH34x_puaWt-KSfMBDOK12a58gYEBRoCHdsQAvD_BwE).

To run any _Dash_ program you do it in the usual way, and follow to the ip address instructed in your command pompt:
  1. open command prompt (or Anaconda Prompt, or Terminal, or whatever)
  2. run `python NAME_OF_YOUR_PROGRAM.py`
For this to work your programs should end with 
```python
if __name__ == '__main__':
    app.run_server(debug=True)
```

The systems included so far are (please do include the instruments you add):

1. Keithley 6221 (current source)
2. HP 34401 (DMM)

