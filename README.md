This is a simple application that uses kivy and python to create a multi-platform GUI application.
# The app is divided into two parts:
1. The GUI
2. The backend

## The GUI

The framework used to create the GUI is kivy.
> The GUI is designed to be interactive and user-friendly with extensive use of buttons and labels and modals.

> This can be achieved by using the kivy language and the kivy framework which provides the necessary widgets and layouts.

>The GUI is designed to be responsive and adaptive to different screen sizes and resolutions to ensure that the app is accessible to all users.

> The GUI will contain multiple embeds to display and visualize data efficiently and effectively.

> Data will be displayed in the form of graphs and charts and where possible it will be formatted to be easily readable and understandable.

> The GUI will also contain a search bar to allow users to search for specific features and data.

> The labels and text displayed on the GUI will be in English and will be translated to other languages using the Google Translate API such that language is not a barrier to accessing the app.

Algorithms to implement the features listed above are:
1. OOP (Object Oriented Programming) will be used to create a robust and scalable application.
2. The graphs and charts will be implemented using the matplotlib library.
3. `deep_translator` lib from pypi will be used to translate the text displayed on the GUI.
4. The GUI will be responsive and adaptive to different screen sizes and resolutions using the kivy language and the kivy framework. Templates for the app will be stored in the `.kv` files.


## The Backend

The backend is planned to be written in python and is responsible for:

> The backend is going to be written in python and it's main purpose is serve as a bridge between the GUI and the API. Thus functioning as an api wrapper.

> The backend will be responsible for making requests to the api and receiving responses from the api.

> The backend is also responsible for processing relevant data organizing and feeding it to the frontend.


Algorithms to implement the features listed above are:
1. A certain extent of GUI development will be done in the backend to ensure that the GUI is responsive and interactive.
2. To achieve the above, OOP is necessary to make effective use of the kivy framework as kivy is an OOP framework. It has it's own object classes and methods which need to be imported and subclassed to create the GUI.
3. Main kivy features to be used in backend are modules from `kivy.app`, `kivy.event`, `kivy.uix` and `kivy.properties`.
4. Anothe important feature to be used in the backend is the `kivy.clock` module which is used to schedule events and functions to be executed at a certain time.
5. The backend also consists of an API wrapper which wraps around our RESTful API and abstracts away the complexity of making requests to the API. This is done using the `requests` library from pypi.
6. The backend will also be responsible for processing data and organizing it in a way that is easy to understand and visualize. This will be done using the `pandas` library from pypi.
7. `dataclasses` will be used to organize data and improve maintainability of code with type hints.
8. `json` will be used to serialize and deserialize data since the API uses JSON as it's data format.
9. `logging` will be used to log errors and exceptions to a file for debugging purposes.
