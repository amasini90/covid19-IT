# covid19-IT
Code to display the Italian percentage of new covid19 cases for a given timespan, relative to new daily tests, as well as the daily variation of people in intensive care unit (ICU) or generally hospitalized with less severe symptoms.
The code reads the data from the official GitHub of the Italian government and nicely displays the relevant quantities.

# Prerequisites
* Numpy (`pip install numpy`)
* Pandas (`pip install pandas`)
* Matplotlib (`pip install matplotlib`)

# Syntax and Usage
Simply run the script with 

`python update_covid_it.py startdate enddate`,

with dates in format `yyyymmdd`.
If you prefer, you can simply use an end date; the code will plot the 30 days prior to the given date (adjustable in the code).
The end date can also be passed as "latest", i.e.

`python update_covid_it.py latest`

will plot the last 30 days data.
