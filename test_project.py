import pytest
from howlongtobeatpy import HowLongToBeat
import re
import requests
import json
import csv
import sys
from tabulate import tabulate
import unittest
import builtins
from unittest.mock import patch, mock_open
from project import get, request, howlong, filename, filecheck,writefile,view_main,table,remove,update


class TestGet(unittest.TestCase):
    def test_get(self):
        with patch.object(
            builtins,
            "input",
            return_value="https://store.steampowered.com/app/1245620/ELDEN_RING/",
        ):
            self.assertEqual(get(), "1245620")
        with patch.object(
            builtins,
            "input",
            return_value="https://store.steampowered.com/app/NO_GAME_ID/",
        ):
            self.assertEqual(get(), False)
        with patch.object(builtins, "input", return_value="RANDOM"):
            self.assertEqual(get(), False)


class TestRequest(unittest.TestCase):
    def test_request(self):

        #getting actual data from API
        gameid = "1174180"
        with patch.object(builtins, "input", return_value="yes"):
            self.assertEqual(request(gameid), request(gameid))
        gameid = "1174181"
        #invalid id
        with patch.object(builtins, "input", return_value="yes"):
            self.assertEqual(request(gameid), False)


def test_howlong():
    assert howlong("fallout: new vegas") == (27.29, 131.57)
    assert howlong("Invalid (NOT A GAME TITLE)") == (0, 0)

class EndError(Exception):
    pass

class TestFilename(unittest.TestCase):
    def test_filename(self):
        with patch.object(builtins, "input", return_value="wishlist.csv"):
            self.assertEqual(filename(), "wishlist.csv")
        with patch.object(builtins, "input", side_effect=["wishlist.py","wishlist","wishlist.csv"]):
            self.assertEqual(filename(), "wishlist.csv")


class TestFileCheck(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="test data")
    def test_filecheck(self, file_name):
        self.assertEqual(filecheck("test_file.csv"),True)
        file_name.side_effect = FileNotFoundError
        self.assertEqual(filecheck("nonexistent.csv"),False)

def test_writefile_and_readtolist():
    expectedlist=[{
                "name":"Star Wars Knights Of The Old Republic",
                "id":"32370",
                "price":"S$10.00",
                "length":"29.11",
                "completionist":"46.84",
                "main price ratio":"2.911",
                "completionist price ratio":"4.684"
            }]
    testlist=[{
                "name":"Star Wars Knights Of The Old Republic",
                "id":"32370",
                "price":"S$10.00",
                "length":"29.11",
                "completionist":"46.84",
                "main price ratio":"2.911",
                "completionist price ratio":"4.684"
            }]
    #writefile
    file= open("test_file.csv", "w")
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "name",
            "id",
            "price",
            "length",
            "completionist",
            "main price ratio",
            "completionist price ratio",
        ],
    )
    writer.writeheader()
    for game in testlist:
        writer.writerow(
            {
                "name": game["name"],
                "id": game["id"],
                "price": game["price"],
                "length": game["length"],
                "completionist": game["completionist"],
                "main price ratio": game["main price ratio"],
                "completionist price ratio": game["completionist price ratio"],
            }
        )
    file.close()
    testlist.clear()
    #readtolist
    file = open("test_file.csv", "r")
    reader = csv.DictReader(file)
    for row in reader:
        testlist.append(
            {
                "name": row["name"],
                "id": row["id"],
                "price": row["price"],
                "length": row["length"],
                "completionist": row["completionist"],
                "main price ratio": row["main price ratio"],
                "completionist price ratio": row["completionist price ratio"],
            }
        )
    file.close()
    assert expectedlist == testlist

def test_view():
    presorted = [
                {"name": "Guilty Gear Strive",
                "id": "1384160",
                "price": "S$52.90",
                "length": "5.08",
                "completionist": "45.68",
                "main price ratio": float(0.09603024574669188),
                "completionist price ratio": float(0.86351606805293),
                },
                #length and completionist length not found on howlongtobeat
                {"name": "Synthetik 2",
                "id": "1471410",
                "price": "S$14.80",
                "length": "0",
                "completionist": "0",
                "main price ratio": float(0.0),
                "completionist price ratio": float(0.0),
                },
                {
                "name":"Star Wars Knights Of The Old Republic",
                "id":"32370",
                "price":"S$10.00",
                "length":"29.11",
                "completionist":"46.84",
                "main price ratio":float(2.911),
                "completionist price ratio":float(4.684)
                }
                ]
    expected = [{
                "Name":"Star Wars Knights Of The Old Republic",
                "Steam ID":"32370",
                "Price":"S$10.00",
                "Main Length":"29.11",
                "Main / Price":float(2.911),
                },
                {"Name": "Guilty Gear Strive",
                "Steam ID": "1384160",
                "Price": "S$52.90",
                "Main Length": "5.08",
                "Main / Price": float(0.09603024574669188),
                },
                {"Name": "Synthetik 2",
                "Steam ID": "1471410",
                "Price": "S$14.80",
                "Main Length": "0",
                "Main / Price": float(0.0),
                },
                ]
    postsorted = view_main(presorted)
    assert postsorted == expected

def test_table():
    newlist = [{
                "Name":"Star Wars Knights Of The Old Republic",
                "Steam ID":"32370",
                "Price":"S$10.00",
                "Main Length":"29.11",
                "Main / Price":float(2.911),
                },
                {"Name": "Guilty Gear Strive",
                "Steam ID": "1384160",
                "Price": "S$52.90",
                "Main Length": "5.08",
                "Main / Price": float(0.09603024574669188),
                },
                {"Name": "Synthetik 2",
                "Steam ID": "1471410",
                "Price": "S$14.80",
                "Main Length": "0",
                "Main / Price": float(0.0),
                },
                ]
    assert (table([])) == "List is empty"
    assert (table(newlist)) == tabulate(
            newlist,
            headers="keys",
            tablefmt="fancy_grid",
            showindex=range(1, len(newlist) + 1),
        )

def test_remove():
    newlist=[{
                "name":"Star Wars Knights Of The Old Republic",
                "Steam ID":"32370",
                "Price":"S$10.00",
                "Main Length":"29.11",
                "Main / Price":float(2.911),
                },
                {"name": "Guilty Gear Strive",
                "Steam ID": "1384160",
                "Price": "S$52.90",
                "Main Length": "5.08",
                "Main / Price": float(0.09603024574669188),
                },
                {"name": "Synthetik 2",
                "Steam ID": "1471410",
                "Price": "S$14.80",
                "Main Length": "0",
                "Main / Price": float(0.0),
                },
                ]
    assert remove("Guilty Gear Strive",newlist) == True
    assert remove("Bubsy 3D",newlist) == False

def test_update():
    response = requests.get(
        "https://store.steampowered.com/api/appdetails?appids=1384160"
    )
    o = response.json()
    expect = o["1384160"]["data"]["price_overview"]["final_formatted"]
    assert update('1384160') == expect