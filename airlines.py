"""
Module to parse the OpenFlights airlines.dat database.

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

AIRLINE_DATA = None
_FIELDNAMES = ('id', 'name', 'alias', 'iata', 'icao', 'callsign', 'country', 'active')


def read(datafile='airlines.dat'):
    """
    Read the datafile into memory.

    :param datafile: Name of the airlines.dat file, defaults to 'airlines.dat'
    """
    global AIRLINE_DATA
    AIRLINE_DATA = dict()
    if not os.path.exists(datafile):
        print(f'Unable to find airline data file "{datafile}". Please download airlines.dat from https://openflights.org/data')
        sys.exit(1)
    with open(datafile, newline='') as csvfile:
        reader = csv.DictReader(csvfile, _FIELDNAMES)
        for row in reader:
            if row['iata'] != '':
                AIRLINE_DATA[row['iata']] = row
            AIRLINE_DATA[row['icao']] = row


def get(code):
    """
    Get an airline's info based on the IATA or ICAO code.

    :param code: code of the airport
    :return: dictionary of airport info
    """
    if AIRLINE_DATA is None:
        read()
    return AIRLINE_DATA[code]
