# imports
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
import PySimpleGUI as sg

# ----------------------------------------- INPUTS -----------------------------------------
column_names = ["Stock Symbol"]
# ------------------------------------------------------------

sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
layout = [  [sg.Text('      '), sg.Text(column_names[0])],
            [sg.Button('+'), sg.InputText()] ]

# Create the Window
window = sg.Window('Window Title', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    print('You entered ', values[0])

window.close()