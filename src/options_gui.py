# imports
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
import tkinter as tk

# -------------------------- INPUTS --------------------------
column_names = ["Stock Symbol","Expiry","Type","Buy/Sell",\
                "Open\nPrice/Share","# Shares",\
                "Current\nPrice/Share","Strike","Premium",\
                "# Contracts","Close\nStrategy",\
                "Close\nPrice/Share","Close\nPremium"\
                "Fee","Profit/Loss",\
                "Net Realized P/L\nFor Underlier",\
                "Status","Account"]
# ------------------------------------------------------------

window = tk.Tk()

# get width x height of display
width= window.winfo_screenwidth() 
height= window.winfo_screenheight()
window.geometry("%dx%d" % (width, height))
window.title("Options Positions")

# configure grid
window.columnconfigure((0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18), weight=1)
window.rowconfigure((0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20), weight=1)

# Create column headers
seriesOffset = 11
col = 0
for label in column_names:
    columnLabel = tk.Label( text=label,\
                            font='"Helvetica Neue" 14 bold')
    columnLabel.grid(column=col, row=seriesOffset)
    col=col+1
window.mainloop()