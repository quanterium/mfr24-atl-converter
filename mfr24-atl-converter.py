#!/usr/bin/env python3

"""
Script to convert CSV export files from MyFlightRadar24 to the TSV format used
for the Air Travel Log iOS app.

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

import airlines
import airports

from great_circle_calculator.great_circle_calculator import distance_between_points

import argparse
import csv
import datetime
import os
import re
import sys
import zoneinfo

CODE_REGEX = re.compile('.+\((.+)\)')


def extract_code(name):
    """
    Extracts and returns the code from the airport or airline name. Provides the IATA code if available, otherwise the ICAO code.

    :param name: Name of the airport or airline in the format "City / Airport Name (IATA/ICAO)" or "Airline Name (IATA/ICAO)"
    :return: IATA or ICAO code
    """
    result = CODE_REGEX.search(name)
    return result.group(1).split('/')[0]


def extract_icao(name):
    """
    Extracts and returns the ICAO code from the airport name.

    :param name: Name of the airport in the format "City / Airport Name (IATA/ICAO)"
    :return: IATA or ICAO code
    """
    result = CODE_REGEX.search(name)
    return result.group(1).split('/')[-1]


def format_time(mfrrow):
    """
    Format and return the departure and arrival dates and times. MyFlightRadar24 export only has the departure date,
    while Air Travel Log's format wants the date with both the departure and arrival time, so we need to calculate the
    arrival date, factoring in timezones and the flight duration.

    :param mfrrow: dict representing a row of MyFlightRadar24 data
    :return: departure and arrival date/times formatted for Air Travel Log
    """
    depart_airport = extract_icao(mfrrow['From'])
    depart_info = airports.get(depart_airport)
    arrive_airport = extract_icao(mfrrow['To'])
    arrive_info = airports.get(arrive_airport)
    deptime = datetime.datetime.strptime(f'{mfrrow["Date"]} {mfrrow["Dep time"]}', '%m/%d/%y %H:%M:%S')
    deptime = deptime.replace(tzinfo=zoneinfo.ZoneInfo(depart_info['timezone']))
    deptime_atl = deptime.strftime('%Y-%m-%d %H:%M')
    duration_tuple = mfrrow['Duration'].split(':')
    duration = datetime.timedelta(seconds=int(duration_tuple[2]),
                                  minutes=int(duration_tuple[1]),
                                  hours=int(duration_tuple[0]))
    arrtime = deptime + duration
    arrtime = arrtime.astimezone(zoneinfo.ZoneInfo(arrive_info['timezone']))
    arrtime_atl = f'{arrtime.strftime("%Y-%m-%d")} {mfrrow["Arr time"].rsplit(":", 1)[0]}'
    return deptime_atl, arrtime_atl


def extract_airline(flightnum):
    """
    Determine the airline and airline code from the flight number.

    :param flightnum: flight number (arline code + number)
    :return: airline name and code formatted for Air Travel Log
    """
    if flightnum[:3].isalpha():
        airline_code = flightnum[:3]
    else:
        airline_code = flightnum[:2]
    airline_info = airlines.get(airline_code)
    return airline_code, airline_info['name']


def extract_aircraft(aircraft):
    """
    Extract the aircraft name and code.

    :param aircraft: Name of the aircraft in the format "Aircraft Name (ICAO)"
    :return: aircraft name and code formatted for Air Travel Log
    """
    code = extract_code(aircraft)
    name = aircraft.split('(')[0].strip()
    return name, code


def format_seat_type(seattype):
    """
    Convert MyFlightRadar24 numeric seat type codes to Air Travel Log code and name.
    
    :param seattype: numeric seat type code
    :return: seat type name and code
    """
    seat_dict = {'0': ('Unknown', 'U'),
                 '1': ('Window', 'W'),
                 '2': ('Middle', 'M'),
                 '3': ('Aisle', 'A')}
    return seat_dict[seattype]


def format_seat_class(seatclass):
    """
    Convert MyFlightRadar24 numeric seat class codes to Air Travel Log code and name.
    
    :param seatclass: numeric seat class code
    :return: seat class name and code
    """
    seat_dict = {'1': ('Economy', 'Y'),
                 '2': ('Business', 'J'),
                 '3': ('First', 'F'),
                 '4': ('Premium Economy', 'W'),
                 '5': ('Private', 'P')}
    return seat_dict[seatclass]


def calculate_distance(mfrrow):
    """
    Calculate the great circle distance in kilometers between the departure and arrival airports.

    :param mfrrow: dict representing a row of MyFlightRadar24 data
    :return: great circle distance in kilometers
    """
    depart_airport = extract_icao(mfrrow['From'])
    depart_info = airports.get(depart_airport)
    arrive_airport = extract_icao(mfrrow['To'])
    arrive_info = airports.get(arrive_airport)
    depart_lat = float(depart_info['latitude'])
    depart_lon = float(depart_info['longitude'])
    arrive_lat = float(arrive_info['latitude'])
    arrive_lon = float(arrive_info['longitude'])
    dist = distance_between_points((depart_lon, depart_lat), (arrive_lon, arrive_lat), 'kilometers', True)
    return dist

def convert(infile, outfile):
    """
    Convert MyFlightRadar24 CSV file to Air Travel Log TSV file.

    :param infile: Name of MyFlightRadar24 CSV file to convert.
    :param outfile: Name of Air Travel Log TSV file to generate.
    """
    atlrows = list()
    with open(infile, newline='') as incsv:
        reader = csv.DictReader(incsv)
        for mfrrow in reader:
            atlrow = dict()
            atlrow['FlightNumber'] = mfrrow['Flight number']
            atlrow['OriginCode'] = extract_code(mfrrow['From'])
            atlrow['DestinationCode'] = extract_code(mfrrow['To'])
            atlrow['DistanceInKm'] = calculate_distance(mfrrow)
            atlrow['STD'], atlrow['STA'] = format_time(mfrrow)
            atlrow['ScheduledDuration'] = mfrrow['Duration'].rsplit(':', 1)[0]
            atlrow['ATD'] = atlrow['STD']  # MyFlightRadar24 doesn't track actual flight times
            atlrow['ATA'] = atlrow['STA']
            atlrow['ActualDuration'] = atlrow['ScheduledDuration']
            atlrow['AirlineCode'], atlrow['AirlineName'] = extract_airline(mfrrow['Flight number'])
            atlrow['Registration'] = mfrrow['Registration']
            atlrow['EquipmentName'], atlrow['EquipmentCode'] = extract_aircraft(mfrrow['Aircraft'])
            atlrow['ManufacturerCode'] = ''
            atlrow['ManufacturerName'] = ''  # no reliable way to extract this as manufacturer can have more than one
                                             # word e.g. McDonnell Douglas, as can the model e.g. EMB-120 Brasilia.
            atlrow['SeatNumber'] = mfrrow['Seat number']
            atlrow['SeatTypeName'], atlrow['SeatTypeCode'] = format_seat_type(mfrrow['Seat type'])
            atlrow['FlightClassName'], atlrow['FlightClassCode'] = format_seat_class(mfrrow['Flight class'])
            atlrow['OperatingCarrierName'], atlrow['OperatingCarrierCode'] = extract_aircraft(mfrrow['Airline'])
            atlrow['IgnoreInStatistics'] = ''
            atlrow['Remark'] = mfrrow['Note']
            atlrows.append(atlrow)
    with open(outfile, 'w', newline='') as outtsv:
        fieldnames = ['FlightNumber', 'OriginCode', 'DestinationCode', 'DistanceInKm', 'STD', 'STA',
                      'ScheduledDuration', 'ATD', 'ATA', 'ActualDuration', 'AirlineCode', 'AirlineName', 'Registration',
                      'EquipmentCode', 'EquipmentName', 'ManufacturerCode', 'ManufacturerName', 'SeatNumber',
                      'SeatTypeCode', 'SeatTypeName', 'FlightClassCode', 'FlightClassName', 'OperatingCarrierCode',
                      'OperatingCarrierName', 'IgnoreInStatistics', 'Remark']
        writer = csv.DictWriter(outtsv, fieldnames=fieldnames, dialect='excel-tab')
        writer.writeheader()
        writer.writerows(atlrows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert MyFlightRadar24 CSV export files to TSV files for import to Air Travel Log.')
    parser.add_argument('infile', help='MyFlightRadar24 CSV file to convert.')
    parser.add_argument('-o', '--outfile', default=None, help='Output filename for Air Travel Log TSV file. If not specified, the anem of the input file will be used with an .atltsv extension.')
    args = parser.parse_args()
    if args.infile is None:
        print('ERROR: Missing input file.')
        sys.exit(1)
    if not os.path.exists(args.infile):
        print(f'ERROR: Specified input file "{args.infile}" was not found.')
        sys.exit(1)
    if args.outfile is None:
        root, _ = os.path.splitext(args.infile)
        args.outfile = root + '.atltsv'
    airports.read()
    airlines.read()
    convert(args.infile, args.outfile)
