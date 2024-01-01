# MyFlightRadar24 - Air Travel Log Converter

This program can be used to convert a CSV export file from [MyFlightRadar24](https://my.flightradar24.com) into a
format suitable for importing into the [Air Travel Log](https://sapientapps.com/airtravellog/) app.

This program is Copyright 2023 David Mueller and released under the GPLv3.

## Usage

The program requires Python 3.9 or later. It also requires the [Great Circle Calculator](https://pypi.org/project/great-circle-calculator/)
package, which can be installed ether in a virtual environment (recommended) or system-wide. Finally, the
[OpenFlights](https://openflights.org/data) airpots.dat and airlines.dat files need to be downloaded to the same
directory where the program is located.

Log in to MyFlightRadar24 and go to the [Export](https://my.flightradar24.com/settings/export) page under Settings.
Click the button to download a CSV file of your flights.

Using the command line (Terminal.app on MacOS), run the script and pass it the name (and path if it's in a different
folder) to the downloaded CSV file:

`$ python3 mfr24-atl-converter.py flightdiary_2023_12_24_08_27.csv`

The converted file will have the same name but with the `.atltsv` file extension. Copy this file to your iCloud Drive,
then on your iPhone, run and exit the Air Travel Log app. Open the Files app and copy the file from iCloud Drive to
On My iPhone/Air Travel Log/Import/FlightData. Finally, open the Air Travel Log app, go to Settings, Advanced Settings,
select Import Flight Data. Tap the name of the file, then in the "Load Import File" popup, click Yes. The import
process may take several minutes to complete.

Once the process is done, you will want to review the conversions and performed potential clean up. Things to look for
are detailed in the "Conversion Notes and Assumptions" section below.

## Conversion Notes and Assumptions

MyFlightRadar24 only has a single departure/arrival time field, which the MyFlightRadar24 site will autocomplete with
the scheduled departure and arrival time after entering the flight number and date. Air Travel Log has fields for both
the scheduled and actual departure and arrival times. This program uses the date and time from the MyFlightRadar24
export as both the scheduled actual times.

MyFlightRadar24 only has a single airline field, while Air Travel Log has fields for the airline and operating airline.
This program derives the airline from the flight number (i.e. AS3308 will be Alaska Airlines) and the operating
airline from the listed airline in the export (i.e. SkyWest Airlines). Airlines are dervied from the OpenFlights
airlines.dat file, and if there are two entries in the file with the same IATA code (i.e. LH for both Lufthansa and
Lufthansa Cargo), it will randomly select one, so it is recommended to review the airlines in the app under Settings,
Master Data-Airlines after importing and make any corrections. Another correction will be for defunct airlines that
have had their code reassigned (i.e. American Trans Air's code TZ was reassigned to Scoot).

The MyFlightRadar24 export includes the departure date and time, but for the arrival includes only the time, plus the
duration of the flight. This program calculates the arrival date by adding the duration to the departure time, adjusting
for the timezones of the departure and arrival airports, in order to determine the arrival date.

The program cannot determine which parts of the aircraft type field indicate the manufacturer and which indicate the
model, so it will not include any manufacturer linkage. These can be added after import in the app under Settings,
Master Data-Equipments.

The flight distance is not included in the MyFlightRadar24 export. It is calculated by this program using the Great
Circle Calculator PIP package, and may not match the calculations made by the app for manually added flights or by
MyFlightRadar24.
