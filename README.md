# covid19-IT
Daily updates on covid19 cases in Italy and display of results

# Prerequisites
Numpy
Pandas
Datetime

# Syntax and Usage
Simply run the script with 
python update_covid_it.py startdate enddate,
with dates in format yyyymmdd.
If you prefer, you can simply use an end date; the code will plot the 30 days prior to the given date (adjustable in the code).
The end date can also be passed as "latest", i.e.
python update_covid_it.py latest
will plot the last 30 days data.
