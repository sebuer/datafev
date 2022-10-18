# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 11:38:18 2022

@author: aytugy
"""

import pandas as pd
import os, sys


def excel_to_sceneration_input(file_path, dependent_times=False):
    """
    This method converts the excel inputs into inputs suitable for the generate_fleet_data function under sceneration.py.

    Parameters
    ----------
    file_path : str
        File path of the Excel input file.
    dependent_times : bool, optional
        Scenario generator has the ability to generate scenarios from two different types of inputs:
            1. Independent arrival and departure times:
                The statistical data of arrival and departure times are independent.
                The user must provide two different independent statistical distribution inputs for both arrival and departure times.
                If the boolean is False:
                    Excel inputs will be converted into appropriate inputs to the scenario function for independent arrival and departure times use.
            2. Dependent arrival and departure times:
                The user must provide a single statistical distribution input for arrival and departure times. 
                The relationship between arrival and departure times is assumed to be predefined in that provided input.
                If the boolean is True:
                    Excel inputs will be converted into appropriate inputs to the scenario function for dependent arrival and departure times use.
        The default is False.

    Returns
    -------
    1. Incase of using independent arrival and departure times:
        arr_times_dict : dict
            Arrival times nested dictionary.
            keys: weekend or weekday,
            values: {keys: time identifier, values: time lower bound, time upper bounds and arrival probabilities}.
        dep_times_dict : dict
            Departure times nested dictionary.
            keys: weekend or weekday,
            values: {keys: time identifier, values: time lower bound, time upper bounds and departure probabilities}.
    2. Incase of using dependent arrival and departure times:
        times_dict : dict
            Arrival-departure time combinations nested dictionary.
            keys: Arrival-departure time combination identifier, values: time upper and lower bounds.
        arr_dep_times_dict : dict
            Arrival-departure time combinations' probabilities nested dictionary.
            keys: Arrival-departure time combination identifier, values: their probabilities.
    arr_soc_dict : dict
        SoC nested dictionaries for arrival.
        keys: SoC Identifier, values: SoC Lower Bounds, SOC Upper Bounds and their probabilities.
    dep_soc_dict : dict
        SoC nested dictionaries for departure.
        keys: SoC Identifier, values: SoC Lower Bounds, SOC Upper Bounds and their probabilities.
    ev_dict : dict
        EV nested dictionary.
        keys: EV models, values: their data and probability.

    """
    
    # Read excel file
    pathname = os.path.dirname(sys.argv[0])        
    full_path = os.path.abspath(pathname) 
    statistic_ev_input_path = os.path.join(full_path, file_path)
    if dependent_times is False:
        dep_times_df = pd.read_excel(statistic_ev_input_path, 'DepartureTime')
        arr_times_df = pd.read_excel(statistic_ev_input_path, 'ArrivalTime')
    else:
        times_df = pd.read_excel(statistic_ev_input_path, 'TimeIDDependentTime')
        arr_dep_times_df = pd.read_excel(statistic_ev_input_path, 'DependentTime')
    arr_soc_df = pd.read_excel(statistic_ev_input_path, 'ArrivalSoC')
    dep_soc_df = pd.read_excel(statistic_ev_input_path, 'DepartureSoC')
    ev_df = pd.read_excel(statistic_ev_input_path, 'EVData')

    if dependent_times is False:
        # Convert percent probabilities to probabilities between 0 and 1
        arr_times_df['WeekdayArrivalPercentage'] = arr_times_df['WeekdayArrivalPercentage'].div(100)
        arr_times_df['WeekendArrivalPercentage'] = arr_times_df['WeekendArrivalPercentage'].div(100)
        dep_times_df['WeekdayDeparturePercentage'] = dep_times_df['WeekdayDeparturePercentage'].div(100)
        dep_times_df['WeekendDeparturePercentage'] = dep_times_df['WeekendDeparturePercentage'].div(100)
        # Separate weekday and weekend arrival/departure times dataframes, rename WeekdayArrivalPercentage to probability
        weekday_arr_times_df = arr_times_df.filter(
            ['TimeID', 'TimeLowerBound', 'TimeUpperBound', 'WeekdayArrivalPercentage'], axis=1)
        weekday_arr_times_df.columns = weekday_arr_times_df.columns.str.replace('WeekdayArrivalPercentage',
                                                                                'Probability')
        weekend_arr_times_df = arr_times_df.filter(
            ['TimeID', 'TimeLowerBound', 'TimeUpperBound', 'WeekendArrivalPercentage'], axis=1)
        weekend_arr_times_df.columns = weekend_arr_times_df.columns.str.replace('WeekendArrivalPercentage',
                                                                                'Probability')
        weekday_dep_times_df = dep_times_df.filter(
            ['TimeID', 'TimeLowerBound', 'TimeUpperBound', 'WeekdayDeparturePercentage'], axis=1)
        weekday_dep_times_df.columns = weekday_dep_times_df.columns.str.replace('WeekdayDeparturePercentage',
                                                                                'Probability')
        weekend_dep_times_df = dep_times_df.filter(
            ['TimeID', 'TimeLowerBound', 'TimeUpperBound', 'WeekendDeparturePercentage'], axis=1)
        weekend_dep_times_df.columns = weekend_dep_times_df.columns.str.replace('WeekendDeparturePercentage',
                                                                                'Probability')
        # Arrival/departure times nested dictionaries
        # keys: weekend or weekday
        # values: {keys: Time Identifier, values: Time Lower Bound, Time Upper Bounds and arrival/departure probabilities}
        arr_times_dict = {}
        weekday_arr_times_df = weekday_arr_times_df.set_index('TimeID')
        arr_times_dict['Weekday'] = weekday_arr_times_df.to_dict(orient='index')
        weekend_arr_times_df = weekend_arr_times_df.set_index('TimeID')
        arr_times_dict['Weekend'] = weekend_arr_times_df.to_dict(orient='index')
        dep_times_dict = {}
        weekday_dep_times_df = weekday_dep_times_df.set_index('TimeID')
        dep_times_dict['Weekday'] = weekday_dep_times_df.to_dict(orient='index')
        weekend_dep_times_df = weekend_dep_times_df.set_index('TimeID')
        dep_times_dict['Weekend'] = weekend_dep_times_df.to_dict(orient='index')
    else:  # if using dependent times
        times_df = times_df.set_index('TimeID')
        times_df['TimeLowerBound'] = times_df['TimeLowerBound'].round('S')
        times_df['TimeUpperBound'] = times_df['TimeUpperBound'].round('S')
        times_dict = times_df.T.to_dict('list')
        arr_dep_times_df = arr_dep_times_df.set_index('TimeID')
        arr_dep_times_dict = {}
        for arr_time_id, row in arr_dep_times_df.iterrows():
            id_list = []
            for dep_time_id, probability in row.items():
                id_list.append(arr_time_id)
                id_list.append(dep_time_id)
                id_tuple = tuple(id_list)
                arr_dep_times_dict[id_tuple] = probability
                id_list.clear()

    # Convert percent SoCs to values between 0 and 1
    arr_soc_df['SoCLowerBound'] = arr_soc_df['SoCLowerBound'].div(100)
    arr_soc_df['SoCUpperBound'] = arr_soc_df['SoCUpperBound'].div(100)
    dep_soc_df['SoCLowerBound'] = dep_soc_df['SoCLowerBound'].div(100)
    dep_soc_df['SoCUpperBound'] = dep_soc_df['SoCUpperBound'].div(100)

    # SoC nested dictionaries for both arrival and departure
    # keys: SoC Identifier, values: SoC Lower Bounds, SOC Upper Bounds and their probabilities
    arr_soc_df = arr_soc_df.set_index('SoCID')
    arr_soc_dict = arr_soc_df.to_dict(orient='index')
    dep_soc_df = dep_soc_df.set_index('SoCID')
    dep_soc_dict = dep_soc_df.to_dict(orient='index')

    # EV nested dictionary
    # keys: EV models, values: their data and probability
    ev_df = ev_df.set_index('Model')
    ev_dict = ev_df.to_dict(orient='index')

    if dependent_times is False:
        return arr_times_dict, dep_times_dict, arr_soc_dict, dep_soc_dict, ev_dict
    else:  # if using dependent times
        return times_dict, arr_dep_times_dict, arr_soc_dict, dep_soc_dict, ev_dict