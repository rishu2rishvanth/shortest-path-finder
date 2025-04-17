# Guide to run shortest_path.py

## Setting up API

     > Login to Google Cloud
    > Navigate to API & services and Enter Library
    > Find and enable "Maps Embeded API"
    > Setup API key filters to prevent unauthorized usage
    > Copy the API Key.

## Creating environment

    > Create .env file
        API_KEY=<YOUR API KEY>
    > Create a python virtual environment "python -m venv venv"
    > Activate the venv enviroment ".\venv\Scripts\Activate"
    > Run "pip install requirements.txt"

## Using shortest_path_V0.py with landmarks in code

    > Add the python file with necessary places and their co-ordinates in tha landmarks
        Example:
            "Hotel Garlica Grand": "14.6794,77.6006",
            "Reliance Digital": "14.6785,77.5997",
    > Run "python shortest_path_V0.py"

## Using shortest_path.py with landmarks in excel

    > Create an excel with name "landmarks.xlsx"
    > Follow below format
<table class="table table-bordered">
  <thead class="thead-light">
    <tr>
      <th>Landmark Name</th>
      <th>Latitude</th>
      <th>Longitude</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>
        <p>Hotel Garlica Grand</p>
      </td>
      <td>
        <p>14.6794</p>
      </td>
      <td>
        <p>77.6006</p>
      </td>
    </tr>
    <tr>
      <td>
        <p>Reliance Digital</p>
      </td>
      <td>
        <p>14.6785</p>
      </td>
      <td>
        <p>77.5997</p>
      </td>
    </tr>
  </tbody>
</table>
    > Run "python shortest_path.py"


# Happy Coding! 