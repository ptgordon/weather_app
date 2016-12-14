from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemButton
from kivy.properties import ObjectProperty, ListProperty, StringProperty, NumericProperty
from kivy.network.urlrequest import UrlRequest
from kivy.factory import Factory
import json


class WeatherRoot(BoxLayout):   #root widget either add location or current weather will be referenced

	current_weather = ObjectProperty()  # ObjectProperty stores the widget

	def show_add_location_form(self):
		self.clear_widgets()
		self.add_widget(AddLocationForm())

	def show_current_weather(self, location=None):  # default shows that none is an option
		self.clear_widgets()

		if location is None and self.current_weather is None:  # if you hit cancel immediately pretend new york was the last entry
			location = ("New York", "US") # this is ugly because it must be updated if the format of the code changes
		if location is not None:
			self.current_weather = CurrentWeather(location=location)
		self.add_widget(self.current_weather)

class AddLocationForm(BoxLayout):  # BoxLayout specifies how it will be interacted with in .kv file
	search_input = ObjectProperty()  # created at class level as an instance of the ObjectProperty class

	def args_converter(self, index, data_item):  #converts data item from tuple to list
		city, country = data_item
		return {'location': (city, country)}

	def search_location(self):
		search_template = "http://api.openweathermap.org/data/2.5/find?q={}&type=like&APPID=e843980d57222bc2a38837d56f83d1cb" # the {} in the URL is a placeholder for the user-s query the str. format is used in the next line to replace the value.
		search_url = search_template.format(self.search_input.text)  #notice how it uses the the search_input ObjectProperty to fill in the blank
		request = UrlRequest(search_url, self.found_location) # fetches data from the url then runs the found_location method

	def found_location(self, request, data):  # the data passed by UrlRequest is a parsed dictionary of JSON code
		data = json.loads(data.decode()) if not isinstance(data, dict) else data # checks if the json list is a dictionary and converts it to one if it isn't already
		cities = [(d['name'], d['sys']['country'])  # this guy is taking the data from the json list and puting it into a new list called cities
			for d in data['list']]
		self.search_results.item_strings = cities  # turns the list into an actual visible list in kivy
		self.search_results.adapter.data.clear()  # first clear the list
		self.search_results.adapter.data.extend(cities) # extend it with the new data
		self.search_results._trigger_reset_populate() # update the display

class LocationButton(ListItemButton):
	location = ListProperty()

class CurrentWeather(BoxLayout):
	location = ListProperty(['New York', 'US'])  # defaults
	conditions = StringProperty()
	temp = NumericProperty()
	temp_min = NumericProperty()
	temp_max = NumericProperty()

	def update_weather(self):
		weather_template = "http://api.openweathermap.org/data/2.5/weather?q={},{}&units=imperial"
		weather_url = weather_template.format(*self.location)
		request =  UrlRequest(weather_url, self.weather_retrieved)

	def weather_retrieved(self, request, data):
		data = json.loads(data.decode()) if not isinstance(data,dict) else data
		self.conditions = data['weather'][0]['description']
		self.temp = data['main']['temp']
		self.temp_min = data['main']['temp_min']
		self.temp_max = data['main']['temp_max']

class WeatherApp(App):
	pass

if __name__ == '__main__':
	WeatherApp().run()
