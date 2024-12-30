from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
import json
import os

class TableApp(FloatLayout):
  SAVE_FILE = "table_data.json"

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

    # Button at the top-left corner
    self.add_row_btn = Button(
      text="New Trade",
      size_hint=(None, None),  # Fixed size
      size=(180, 80),         # Button dimensions
      pos_hint={"x": 0.05, "top": 0.98}  # Top-left corner
    )
    self.add_row_btn.bind(on_press=self.open_add_row_popup)
    self.add_widget(self.add_row_btn)

    # Create a scrollable area for the table (including the header)
    self.scroll_view = ScrollView(
      size_hint=(1, 0.77),
      pos_hint={"x": 0, "y": 0.1}
    )

    # Create a grid layout for the table
    self.table = GridLayout(
      cols=13,
      size_hint_y=None,  # Allow dynamic height
      height=50  # Start with the height of the header row
    )

    # Add the header row directly into the table
    for header in [
      "Ticker", "Open\nDate", "Expiry", "Type", "Open", "Strike", "Underlier", 
      "Premium", "Fee", "Qnt", "Close", "Close\nPremium", "P/L"
    ]:
      self.table.add_widget(Label(
        text=header, bold=True, halign="center", valign="middle",
        text_size=(None, None), size_hint_y=None, height=60
      ))

    self.scroll_view.add_widget(self.table)
    self.add_widget(self.scroll_view)

    # Load table state from file
    self.load_table_state()

  def open_add_row_popup(self, instance):
    """Opens a popup to prompt the user for row values."""
    popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

    # Create a scrollable area for the input fields
    scroll_view = ScrollView(size_hint=(1, 0.8))
    input_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
    input_layout.bind(minimum_height=input_layout.setter('height'))

    # Input fields for the thirteen columns
    self.inputs = [
      TextInput(hint_text=header, multiline=False, size_hint_y=None, height=50)
      for header in [
        "Ticker", "Open Date", "Expiry", "Type", "Open", "Strike", 
        "Premium", "Fee", "Qnt", "Close", "Close Premium"
      ]
    ]

    for input_field in self.inputs:
      input_layout.add_widget(input_field)

    scroll_view.add_widget(input_layout)
    popup_layout.add_widget(scroll_view)

    # Buttons for submission and cancellation
    button_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
    submit_btn = Button(text="Submit", size_hint=(1, None))
    submit_btn.bind(on_press=self.add_row_from_popup)
    cancel_btn = Button(text="Cancel", size_hint=(1, None))
    cancel_btn.bind(on_press=lambda x: self.popup.dismiss())

    button_layout.add_widget(submit_btn)
    button_layout.add_widget(cancel_btn)
    popup_layout.add_widget(button_layout)

    # Create and open the popup
    self.popup = Popup(title="Add Row", content=popup_layout, size_hint=(0.8, 0.8))
    self.popup.open()

  def add_row_from_popup(self, instance):
    """Adds a new row with user-provided values from the popup."""
    row_values = [input_field.text if input_field.text else "" for input_field in self.inputs]

    # Add new row values
    for value in row_values:
      self.table.add_widget(Label(text=value))

    # Dynamically increase the table height for each row
    row_height = 50  # Adjust based on your row size
    self.table.height += row_height

    # Save state after adding a row
    self.save_table_state()

    # Dismiss the popup
    self.popup.dismiss()

  def save_table_state(self):
    """Saves the current table state to a file."""
    table_data = []
    for widget in self.table.children[::-1]:  # Reverse order to get rows in correct sequence
      if isinstance(widget, Label):
        table_data.append(widget.text)

    # Group table data into rows of 13 (columns per row)
    grouped_data = [table_data[i:i+13] for i in range(0, len(table_data), 13)]

    with open(self.SAVE_FILE, "w") as f:
      json.dump(grouped_data, f)

  def load_table_state(self):
    """Loads the table state from a file if it exists."""
    if os.path.exists(self.SAVE_FILE):
      with open(self.SAVE_FILE, "r") as f:
        table_data = json.load(f)

      for row in table_data:
        for cell in row:
          self.table.add_widget(Label(text=cell))

        # Dynamically increase the table height for each row
        self.table.height += 50

class MyKivyApp(App):
  def build(self):
    self.title = "Trading Table"
    from kivy.core.window import Window
    Window.size = (900, 600)  # Set the default application window size

    return TableApp()

if __name__ == "__main__":
  MyKivyApp().run()
