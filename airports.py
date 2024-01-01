"""
Module to parse the OpenFlights airports.dat database.

Copyright 2023 David Mueller

This file is part of MyFlightRadar24 - Air Travel Log Converter.

MyFlightRadar24 - Air Travel Log Converter is free software: you can redistribute it and/or modify it under the terms
of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Foobar is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with MyFlightRadar24 - Air Travel Log Converter.
If not, see <https://www.gnu.org/licenses/>.
"""

import csv
import os
import sys

AIRPORT_DATA = None
_FIELDNAMES = ('id', 'name', 'city', 'country', 'iata', 'icao', 'latitude', 'longitude', 'altitude', 'offset', 'dst', 'timezone', 'type', 'source')


def read(datafile='airports.dat'):
    """
    Read the datafile into memory.

    :param datafile: Name of the airports.dat file, defaults to 'airports.dat'
    """
    global AIRPORT_DATA
    AIRPORT_DATA = dict()
    if not os.path.exists(datafile):
        print(f'Unable to find airport data file "{datafile}". Please download airports.dat from https://openflights.org/data')
        sys.exit(1)
    with open(datafile, newline='') as csvfile:
        reader = csv.DictReader(csvfile, _FIELDNAMES)
        for row in reader:
            AIRPORT_DATA[row['icao']] = row


def get(icao):
    """
    Get an airport's info based on the ICAO code.

    :param icao: ICAO code of the airport
    :return: dictionary of airport info
    """
    global AIRPORT_DATA
    if AIRPORT_DATA is None:
        read()
    return AIRPORT_DATA[icao]
