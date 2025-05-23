import json
import os
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock

# Set a proper path to save file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EQUITY_SAVE_FILE = os.path.join(SCRIPT_DIR, "./../.etrades.json")
OPTION_SAVE_FILE = os.path.join(SCRIPT_DIR, "./../.otrades.json")

class CloseOptionPositionPopup(Popup):
    def __init__(self, otrade_table, row_index, **kwargs):
        super().__init__(title="Close Option Position", size_hint=(0.7, 0.5), **kwargs)
        self.otrade_table = otrade_table
        self.row_index = row_index

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Input Fields
        self.inputs = {}
        fields = ["Close Price", "Close Premium"]
        for field in fields:
            box = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
            label = Label(text=f"{field}:", size_hint_x=0.4)
            text_input = TextInput(multiline=False)
            self.inputs[field] = text_input
            box.add_widget(label)
            box.add_widget(text_input)
            layout.add_widget(box)

        # Buttons
        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=20)
        confirm_button = Button(text="Confirm", on_press=self.confirm_close_position)
        cancel_button = Button(text="Cancel", on_press=self.dismiss)
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)
        layout.add_widget(button_layout)

        self.content = layout

    def confirm_close_position(self, instance):
        """Validate input, update row with sell details, and compute P/L."""
        try:
            close_text = self.inputs["Close Price"].text.strip()
            close_prem_text = self.inputs["Close Premium"].text.strip()

            try:
                close = float(close_text)
                close_prem = float(close_prem_text)
            except ValueError:
                print("Close Price and Close Premium must be valid numbers.")
                return

            if close <= 0 or close_prem <= 0:
                print("Close Price and Close Premium must be greater than 0.")
                return

            self.otrade_table.close_position(self.row_index, close, close_prem)
            self.dismiss()

        except Exception as e:
            print(f"Unexpected error: {str(e)}")

class ClosePositionPopup(Popup):
    def __init__(self, trade_table, row_index, **kwargs):
        super().__init__(title="Close Position", size_hint=(0.7, 0.5), **kwargs)
        self.trade_table = trade_table
        self.row_index = row_index

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Input Fields
        self.inputs = {}
        fields = ["Sell Date", "Sell Price"]
        for field in fields:
            box = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
            label = Label(text=f"{field}:", size_hint_x=0.4)
            text_input = TextInput(multiline=False)
            self.inputs[field] = text_input
            box.add_widget(label)
            box.add_widget(text_input)
            layout.add_widget(box)

        # Buttons
        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=20)
        confirm_button = Button(text="Confirm", on_press=self.confirm_close_position)
        cancel_button = Button(text="Cancel", on_press=self.dismiss)
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)
        layout.add_widget(button_layout)

        self.content = layout

    def confirm_close_position(self, instance):
        """Validate input, update row with sell details, and compute P/L."""
        try:
            sell_date = self.inputs["Sell Date"].text.strip()
            sell_price_text = self.inputs["Sell Price"].text.strip()

            if not sell_date:
                print("Sell Date cannot be empty.")
                return

            try:
                sell_price = float(sell_price_text)
            except ValueError:
                print("Sell Price must be a valid number.")
                return

            if sell_price <= 0:
                print("Sell Price must be greater than 0.")
                return

            self.trade_table.close_position(self.row_index, sell_date, sell_price)
            self.dismiss()

        except Exception as e:
            print(f"Unexpected error: {str(e)}")

class OptionTable(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(cols=14, row_force_default=True, row_default_height=40, spacing=5, size_hint_y=None, **kwargs)
        self.bind(minimum_height=self.setter('height'))
        self.trade_rows = []

        headers = [
            "Underlier", "Date", "Expiry", "Type", "Open", "Strike",
            "Underlier Price", "Premium", "Fee", "Quantity", "Close", "Close Premium", "P/L", "Action"
        ]
        for header in headers:
            label = Label(
                text=header,
                bold=True,
                size_hint_y=None,
                height=40,
                padding_x=10,  
                halign="center",  
                valign="middle"   
            )
            label.bind(size=label.setter('text_size'))  # Ensure text stays within the label
            self.add_widget(label)

        self.load_trades()

    def add_trade(self, trade_data):
        """Add a new option trade row to the table."""
        row_widgets = []

        for data in trade_data:
            label = Label(
                text=str(data),
                size_hint_y=None,
                height=40,
                padding_x=10,  
                halign="center",  
                valign="middle"  
            )
            label.bind(size=label.setter('text_size'))  # Ensure text stays within the label
            self.add_widget(label)
            row_widgets.append(label)

        # Ensures a vertical layout for the "Action" column
        action_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=40,
            spacing=5
        )

        # Add "Close Position" button
        close_btn = Button(text="Close Position", size_hint_y=None, height=40)
        close_btn.bind(on_press=lambda instance, index=len(self.trade_rows): self.open_close_position_popup(index=index))
        action_layout.add_widget(close_btn)

        self.add_widget(action_layout)
        row_widgets.append(action_layout)

        # Store row for updating later
        self.trade_rows.append(row_widgets)

        # Update table height
        self.height = len(self.trade_rows) * 40 + 40

        # Defer the scroll adjustment until after the widget is added to the parent layout
        Clock.schedule_once(self.adjust_scroll)

        # Refresh UI
        self.canvas.ask_update()

    def open_close_position_popup(self, index):
        """Open the Close Option Position popup."""
        popup = CloseOptionPositionPopup(self, index)
        popup.open()

    def close_position(self, index, close, close_prem):
        """Close position, update sell details, and compute P/L."""
        try:
            row_widgets = self.trade_rows[index]

            # Update Close Price and Close Premium
            row_widgets[10].text = f"{close:.2f}"
            row_widgets[11].text = f"{close_prem:.2f}"

            # Calculate P/L
            open_price = float(row_widgets[4].text)
            premium = float(row_widgets[7].text)
            fee = float(row_widgets[8].text)
            quantity = int(row_widgets[9].text)

            pl = (close - open_price) * (quantity * 100) - fee 
            row_widgets[12].text = f"{pl:.2f}"

            # Highlight P/L (Green = Gain, Red = Loss)
            row_widgets[12].color = (0, 1, 0, 1) if pl > 0 else (1, 0, 0, 1)

            print(f"Option trade at index {index} closed successfully.")
        except Exception as e:
            print(f"Error closing option position: {e}")

    def save_trades(self):
        """Save option trades to a JSON file."""
        trades = []
        for row_widgets in self.trade_rows:
            trade_data = []
            for widget in row_widgets[:-1]:  # Exclude the "Close Position" button
                trade_data.append(widget.text)
            trades.append(trade_data)

        with open(OPTION_SAVE_FILE, 'w') as f:
            json.dump(trades, f)
        print(f"Option trades saved to {OPTION_SAVE_FILE}")

    def load_trades(self):
        """Load option trades from a JSON file."""
        if os.path.exists(OPTION_SAVE_FILE):
            try:
                with open(OPTION_SAVE_FILE, 'r') as f:
                    trades = json.load(f)
                for trade in trades:
                    self.add_trade(trade)
                print(f"Option trades loaded from {OPTION_SAVE_FILE}")
            except json.JSONDecodeError:
                print(f"Error: {OPTION_SAVE_FILE} contains invalid JSON. Starting with an empty table.")
                trades = []
        else:
            print(f"No save file found at {OPTION_SAVE_FILE}")

    def adjust_scroll(self, dt):
        """Adjust the scroll position to the top."""
        if self.parent and self.parent.parent:
            self.parent.parent.scroll_y = 1

class TradeTable(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(cols=9, row_force_default=True, row_default_height=40, spacing=5, size_hint_y=None, **kwargs)
        self.bind(minimum_height=self.setter('height'))
        self.trade_rows = []

        # Table Headers
        headers = ["Ticker", "Buy Date", "Buy Price", "Num Shares", "Notional", "Sell Date", "Sell Price", "P/L", "Action"]
        for header in headers:
            label = Label(text=header, bold=True, size_hint_y=None, height=40)
            self.add_widget(label)

        self.load_trades()  # Load trades on startup

    def add_trade(self, trade_data):
        """Add a new trade row to the table."""
        row_widgets = []

        for data in trade_data:
            label = Label(
                text=str(data),
                size_hint_y=None,
                height=40,
                padding_x=10,  # Add horizontal padding
                halign="center",  # Center-align text
                valign="middle"  # Middle-align text
            )
            label.bind(size=label.setter('text_size'))  # Ensure text wraps within the label
            self.add_widget(label)
            row_widgets.append(label)

        # Add a vertical layout for the "Action" column
        action_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=40,
            spacing=5
        )

        # Add "Close Position" button
        close_btn = Button(text="Close Position", size_hint_y=None, height=40)
        close_btn.bind(on_press=lambda instance, index=len(self.trade_rows): self.open_close_position_popup(index))
        action_layout.add_widget(close_btn)

        self.add_widget(action_layout)
        row_widgets.append(action_layout)

        # Store row for updating later
        self.trade_rows.append(row_widgets)

        # Update table height
        self.height = len(self.trade_rows) * 40 + 40

        # Defer the scroll adjustment until after the widget is added to the parent layout
        Clock.schedule_once(self.adjust_scroll)

        # Refresh UI
        self.canvas.ask_update()

    def adjust_scroll(self, dt):
        """Adjust the scroll position to the top."""
        if self.parent and self.parent.parent:
            self.parent.parent.scroll_y = 1

    def open_close_position_popup(self, row_index):
        """Open the Close Position popup."""
        row_widgets = self.trade_rows[row_index]

        buy_price = row_widgets[2].text
        if buy_price == "-":
            print("Invalid Operation: Cannot sell before buying.")
            return

        popup = ClosePositionPopup(self, row_index)
        popup.open()

    def close_position(self, row_index, sell_date, sell_price):
        """Close position, update sell details, and compute P/L."""
        try:
            row_widgets = self.trade_rows[row_index]

            # Remove any non-numeric formatting
            buy_price_text = row_widgets[2].text.strip()
            try:
                buy_price = float(buy_price_text)
            except ValueError:
                print("Conversion Error: Could not convert Buy Price to a number.")
                return

            # Update Sell Date and Sell Price
            row_widgets[5].text = sell_date
            row_widgets[6].text = f"{sell_price:.2f}"

            # Calculate P/L
            num_shares = int(row_widgets[3].text)
            pl = (sell_price - buy_price) * num_shares
            row_widgets[7].text = f"{pl:.2f}"

            # Highlight P/L (Green = Gain, Red = Loss)
            row_widgets[7].color = (0, 1, 0, 1) if pl > 0 else (1, 0, 0, 1)

            print(f"Equity trade at index {row_index} closed successfully.")
        except Exception as e:
            print(f"Error closing equity position: {e}")

    def save_trades(self):
        """Save trades to a JSON file."""
        trades = []
        for row_widgets in self.trade_rows:
            trade_data = []
            for widget in row_widgets[:-1]:  # Exclude the "Close Position" button
                trade_data.append(widget.text)
            trades.append(trade_data)
        
        with open(EQUITY_SAVE_FILE, 'w') as f:
            json.dump(trades, f)
        print(f"Trades saved to {EQUITY_SAVE_FILE}")

    def load_trades(self):
        """Load trades from a JSON file."""
        if os.path.exists(EQUITY_SAVE_FILE):
            try:
                with open(EQUITY_SAVE_FILE, 'r') as f:
                    trades = json.load(f)
                for trade in trades:
                    self.add_trade(trade)
                print(f"Trades loaded from {EQUITY_SAVE_FILE}")
            except json.JSONDecodeError:
                print(f"Error: {EQUITY_SAVE_FILE} contains invalid JSON. Starting with an empty table.")
                trades = []
        else:
            print(f"No save file found at {EQUITY_SAVE_FILE}")


class AddTradePopup(Popup):
    def __init__(self, trade_table, **kwargs):
        super().__init__(title="Add Trade", size_hint=(0.7, 0.7), **kwargs)
        self.trade_table = trade_table

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Input Fields
        self.inputs = {}
        fields = ["Ticker", "Buy Date", "Buy Price", "Num Shares"]
        for field in fields:
            box = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
            label = Label(text=f"{field}:", size_hint_x=0.4)
            text_input = TextInput(multiline=False)
            self.inputs[field] = text_input
            box.add_widget(label)
            box.add_widget(text_input)
            layout.add_widget(box)

        # Buttons
        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=20)
        confirm_button = Button(text="Confirm", on_press=self.confirm_trade)
        cancel_button = Button(text="Cancel", on_press=self.dismiss)
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)
        layout.add_widget(button_layout)

        self.content = layout

    def confirm_trade(self, instance):
        """Validate input, calculate Notional, and add trade to the table."""
        try:
            ticker = self.inputs["Ticker"].text.strip().upper()
            buy_date = self.inputs["Buy Date"].text.strip()
            buy_price = float(self.inputs["Buy Price"].text)
            num_shares = int(self.inputs["Num Shares"].text)
            notional = round(buy_price * num_shares, 2)

            trade_data = [ticker, buy_date, f"{buy_price:.2f}", str(num_shares), f"{notional:.2f}", "-", "-", "-"]
            self.trade_table.add_trade(trade_data)
            self.dismiss()

        except ValueError:
            print("Invalid Input: Ensure numeric fields contain valid numbers.")

class AddOptionTradePopup(Popup):
    def __init__(self, otrade_table, **kwargs):
        super().__init__(title="Add Option Trade", size_hint=(0.7, 0.7), **kwargs)
        self.otrade_table = otrade_table

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Input Fields
        self.inputs = {}
        fields = ["Underlier", "Date", "Expiry", "Type", "Open Price", "Strike Price", "Underlier Price", "Premium", "Fee", "Quantity"]
        for field in fields:
            box = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
            label = Label(text=f"{field}:", size_hint_x=0.4)
            text_input = TextInput(multiline=False)
            self.inputs[field] = text_input
            box.add_widget(label)
            box.add_widget(text_input)
            layout.add_widget(box)

        # Buttons
        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=20)
        confirm_button = Button(text="Confirm", on_press=self.confirm_trade)
        cancel_button = Button(text="Cancel", on_press=self.dismiss)
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)
        layout.add_widget(button_layout)

        self.content = layout

    def confirm_trade(self, instance):
        """Validate input, calculate Notional, and add trade to the options table."""
        try:
            underlier = self.inputs["Underlier"].text.strip().upper()
            date = self.inputs["Date"].text.strip()
            expiry = self.inputs["Expiry"].text.strip()
            type_ = self.inputs["Type"].text.strip().upper()
            open_price = float(self.inputs["Open Price"].text)
            strike_price = float(self.inputs["Strike Price"].text)
            underlier_price = float(self.inputs["Underlier Price"].text)
            premium = float(self.inputs["Premium"].text)
            fee = float(self.inputs["Fee"].text)
            quantity = int(self.inputs["Quantity"].text)

            trade_data = [
                underlier, date, expiry, type_, f"{open_price:.2f}", f"{strike_price:.2f}",
                f"{underlier_price:.2f}", f"{premium:.2f}", f"{fee:.2f}", str(quantity), "-", "-", "-"
            ]
            self.otrade_table.add_trade(trade_data)
            self.dismiss()

        except ValueError:
            print("Invalid Input: Ensure numeric fields contain valid numbers.")


class MainWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.add_trade_button = Button(text="Add Equity Trade", size_hint=(1, 0.1), on_press=self.open_add_etrade_popup)
        self.add_widget(self.add_trade_button)

        self.escroll = ScrollView(size_hint=(1, 0.9))
        self.etable = TradeTable()
        self.escroll.add_widget(self.etable)
        self.add_widget(self.escroll)

        self.add_otrade_button = Button(text="Add Option Trade", size_hint=(1, 0.1), on_press=self.open_add_otrade_popup)
        self.add_widget(self.add_otrade_button)

        self.oscroll = ScrollView(size_hint=(1, 0.9))
        self.otable = OptionTable()
        self.oscroll.add_widget(self.otable)
        self.add_widget(self.oscroll)

    def open_add_etrade_popup(self, instance):
        popup = AddTradePopup(self.etable)
        popup.open()

    def open_add_otrade_popup(self, instance):
        popup = AddOptionTradePopup(self.otable)
        popup.open()


class TradeApp(App):
    def build(self):
        Window.bind(on_close=self.on_window_close)  # Bind window close event
        return MainWindow()

    def on_stop(self):
        """Save trades when the app closes."""
        self.root.etable.save_trades()
        self.root.otable.save_trades()


    def on_window_close(self, *args):
        """Save trades when the window is closed."""
        self.root.etable.save_trades()
        self.root.otable.save_trades()



if __name__ == "__main__":
    TradeApp().run()

