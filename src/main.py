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
SAVE_FILE = os.path.join(SCRIPT_DIR, "./../.trades.json")


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
            label = Label(text=str(data), size_hint_y=None, height=40)
            self.add_widget(label)
            row_widgets.append(label)

        # Add "Close Position" button
        close_btn = Button(text="Close Position", size_hint_y=None, height=40)
        close_btn.bind(on_press=lambda instance, index=len(self.trade_rows): self.open_close_position_popup(index))
        self.add_widget(close_btn)
        row_widgets.append(close_btn)

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

    def save_trades(self):
        """Save trades to a JSON file."""
        trades = []
        for row_widgets in self.trade_rows:
            trade_data = []
            for widget in row_widgets[:-1]:  # Exclude the "Close Position" button
                trade_data.append(widget.text)
            trades.append(trade_data)
        
        with open(SAVE_FILE, 'w') as f:
            json.dump(trades, f)
        print(f"Trades saved to {SAVE_FILE}")

    def load_trades(self):
        """Load trades from a JSON file."""
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r') as f:
                trades = json.load(f)
            for trade in trades:
                self.add_trade(trade)
            print(f"Trades loaded from {SAVE_FILE}")
        else:
            print(f"No save file found at {SAVE_FILE}")


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


class MainWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.add_trade_button = Button(text="Add Trade", size_hint=(1, 0.1), on_press=self.open_add_trade_popup)
        self.add_widget(self.add_trade_button)

        self.scroll = ScrollView(size_hint=(1, 0.9))
        self.table = TradeTable()
        self.scroll.add_widget(self.table)
        self.add_widget(self.scroll)

    def open_add_trade_popup(self, instance):
        popup = AddTradePopup(self.table)
        popup.open()


class TradeApp(App):
    def build(self):
        Window.bind(on_close=self.on_window_close)  # Bind window close event
        return MainWindow()

    def on_stop(self):
        """Save trades when the app closes."""
        self.root.table.save_trades()

    def on_window_close(self, *args):
        """Save trades when the window is closed."""
        self.root.table.save_trades()


if __name__ == "__main__":
    TradeApp().run()

