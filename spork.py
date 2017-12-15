#!/usr/bin/env python3

import os
from ciscosparkapi import CiscoSparkAPI, SparkApiError
from random import randint
import time
import click
import datetime
import json
import pickle
import csv
from tqdm import tqdm
import progressbar

__author__ = "SomeClown"
__license__ = "MIT"
__maintainer__ = "Teren Bryson"
__email__ = "teren@packetqueue.net"


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
EPILOG = 'Have a fun time throwing foo\'s at bars'

spark_token = os.environ["SPARK_ACCESS_TOKEN"]
api = CiscoSparkAPI()

color_black2 = "\033[1;30m"
color_red2_on = "\033[01;31m"
color_red2_off = "\33[00m"
color_green2 = "\033[1;32m"
color_yellow2 = "\033[1;33m"
color_blue2 = "\033[1;34m"
color_purple2 = "\033[1;35m"
color_cyan2 = "\033[1;36m"
color_white2 = "\033[1;37m"
color_off = "\33[00m"


@click.group(epilog=EPILOG, context_settings=CONTEXT_SETTINGS)
def cli():
    """
    Quick and dirty proof of concept. Exercises the Spark API without killing any kittens.
    :return: 
    """
    pass


@click.command(short_help='Spam a foo', help='#KeepCalmAndSpamOn')
@click.argument('channel', metavar='[channel]')
@click.argument('spam_file', metavar='[file]')
def fortune_spam(channel, spam_file):
    """
    The much vaunted 'spam' option.
    
    :param channel: Which room to send to
    :param spam_file: Which file to pull fortunes from
    :return: 
    """
    test_room = api.rooms.create(channel)
    parsed_fortunes = []
    n = 0
    try:
        with open(spam_file, 'r') as f:
            temp_fortunes = f.read().split('%')
            for item in temp_fortunes:
                parsed_fortunes.append(item.split('%'))

        for item in parsed_fortunes:
            for a, b in enumerate(item):
                item[a] = b.replace('\n', ' ')

        while n <= len(parsed_fortunes) - 1:
            rand_timer = randint(600, 1800)
            rand_item = randint(0, len(parsed_fortunes) - 1)
            message = ''.join(parsed_fortunes[rand_item])
            api.messages.create(test_room.id, text=message)
            print(message)
            n += n
            time.sleep(rand_timer)
    except BaseException as e:
        print('Not sure what shit the bed, but the shit looks like this:')
        print(color_red2_on + str(e) + color_red2_off)


@click.command(options_metavar='[no options]', short_help='return a list of channels')
def retrieve_rooms():
    """
    Returns a list of rooms the user is a part of, or spaces, or whatever we're calling it today
    :return: 
    """
    all_rooms = api.rooms.list()
    rooms_dict = {}
    try:
        for room in all_rooms:
            dt = datetime.datetime.strptime(room.lastActivity, "%Y-%m-%dT%H:%M:%S.%fZ")
            rm = room.title
            rooms_dict[str(dt.date())] = rm
    except SparkApiError as e:
        print(e)
    for k, v in rooms_dict.items():
        print(color_red2_on + '{:45}'.format(v) + color_red2_off +
              '--' + color_blue2 + 'Last Activity: ' + color_yellow2 + str(k))


def get_my_rooms():
    """
    Returns a list of rooms by ID
    :return: 
    """
    rooms = [room for room in api.rooms.list()]
    for room in rooms:
        yield room


def get_my_rooms_lst():
    """
    Returns a list of rooms by ID
    :return: 
    """
    rooms = [room for room in api.rooms.list()]
    return rooms


def get_room_msg(room_id=''):
    """
    Returns messages from a given room ID
    :param room_id: 
    :return: 
    """
    room_messages = [item for item in api.messages.list(roomId=room_id) if item.files is not None]
    for msg in room_messages:
        yield msg


def get_room_msg_lst(room_id=''):
    """
    Returns messages from a given room ID
    :param room_id: 
    :return: 
    """
    room_messages = [item for item in api.messages.list(roomId=room_id) if item.files is not None]
    return room_messages


def flatten(lst: list):
    """
    Not used at this point. Flattens a nested list
    :param lst:
    :return:
    """
    for element in lst:
        if hasattr(element, "__iter__"):
            yield from flatten(element)
        elif element is not None:
            yield element


def save_files(data: dict, file_name: str, file_type: str):
    """
    Save data to file in a variety of formats
    :param data: dictionary
    :param file_name: file name
    :param file_type: one of json, text, csv, pickle
    :return: 
    """
    if file_type == 'json':
        name = json.dumps(data)
        with open(file_name, 'w') as f:
            f.write(name)
    elif file_type == 'pkl':
        with open(file_name, 'wb') as f:
            pickle.dump(data, f)
    elif file_type == 'csv':
        file = csv.writer(open(file_name, "w"))
        for key, value in data.items():
            file.writerow([key, value])


@click.command(options_metavar='[no options]', short_help='get list of files')
def get_all_files_list():
    """
    Returns a list of file attachments in room(s)
    :return: 
    """
    start = time.time()
    rooms_dict = {}

    for room in get_my_rooms():
        msg_list = get_room_msg_lst(room.id)
        files_temp = []
        for item in msg_list:
            files_temp.append(item.files)
        rooms_dict[room.id] = (len(msg_list), room.title, files_temp)
    for key, _ in rooms_dict.items():
        print(key, _)
    save_files(rooms_dict, file_type='json', file_name='all_files.json')
    finish = time.time()
    elapsed = finish - start
    print('\nElapsed time: ' + '{:.2f}'.format(elapsed) + ' seconds')

cli.add_command(get_all_files_list, 'files')
cli.add_command(fortune_spam, 'spam')
cli.add_command(retrieve_rooms, 'rooms')

if __name__ == '__main__':
    try:
        cli()
    except TypeError as err:
        print('Not sure what shit the bed, but we\'ll blame it on you. The error is below:')
        print(color_red2_on + str(err) + color_red2_off)