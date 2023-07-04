# libraries
from howlongtobeatpy import HowLongToBeat
import re
import requests
import json
import csv
import sys
from tabulate import tabulate

newlist = []

#appends game data from steam and howlongtobeat API to newlist
def getandrequest():
    while True:
        try:
            gameid = get()
            if gameid == False:
                pass
            else:
                gamedata = request(gameid)
                if gamedata == False:
                    pass
                else:
                    newlist.append(gamedata)
        except EOFError:
            break

#checks input for valid steam url
def get():
    while True:
        try:
            url = input("Enter Steam game URL (CTRL+D to stop inputting): ")
            matches = re.search(
                r"^https?://store\.(?:steampowered|steamgames)\.com/app/([0-9]+)[^\.]*$",
                url,
                re.IGNORECASE,
            )
            if matches:
                return matches.group(1)
            else:
                return False
        except EOFError:
            raise EOFError

#requests game data from steam and howlongtobeat API
def request(gameid):
    response = requests.get(
        "https://store.steampowered.com/api/appdetails?appids=" + gameid
    )
    o = response.json()
    #checks if the game ID is valid
    if {o[gameid]["success"]} == {True}:
        confirm = (
            input(f"Add {o[gameid]['data']['name']} to your wishlist? (yes / no) ")
            .strip()
            .lower()
        )
        if confirm == "yes":
            name = re.sub(r"([^a-zA-Z0-9_ \:])", "", o[gameid]["data"]["name"])
            price = o[gameid]["data"]["price_overview"]["final_formatted"]
            length, completionist = howlong(name)
            p = re.findall(r"[0-9]+\.?[0-9]*", price.replace(",", ""))
            p = float(*p)
            return {
                "name": name.title(),
                "id": gameid,
                "price": price,
                "length": length,
                "completionist": completionist,
                "main price ratio": f"{length / p:.2f}",
                "completionist price ratio": f"{completionist / p:.2f}",
            }
        else:
            return False
    else:
        return False

#getting the game's length, called from request(gameid)
def howlong(name):
    try:
        results_list = HowLongToBeat().search(name.capitalize())
        if results_list is not None and len(results_list) > 0:
            best_element = max(results_list, key=lambda element: element.similarity)
        else:
            best_element = results_list[(len(results_list))]
    except (IndexError, UnboundLocalError, ValueError):
        return (0, 0)
    else:
        return (best_element.main_story, best_element.completionist)

#checks if the file's extension is valid (.csv)
def filename():
    while True:
        try:
            file_name = input("File Name: ").strip()
            if file_name.endswith(".csv") == False:
                print("File format not supported")
                pass
            else:
                break
        except EOFError:
            sys.exit("Exiting Program...")
    return file_name

#check if file exists, used for edit and view
def filecheck(file_name):
    try:
        file = open(file_name, "r")
        return True
    except FileNotFoundError:
        return False

#writes newlist to a .csv file
def writefile(file_name):
    file = open(file_name, "w")
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
    for game in newlist:
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

#reads from a csv file to newlist
def readtolist(file_name):
    file = open(file_name, "r")
    reader = csv.DictReader(file)
    for row in reader:
        newlist.append(
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

#function that runs to request a list of games, then outputs onto a .csv file
def newfile():
    file_name = filename()
    getandrequest()
    writefile(file_name)

#view prints out tabulate of current list, provides several options for sorting the list
def view():
    try:
        file_name = filename()
        if filecheck(file_name):
            file = open(file_name, "r")
            reader = csv.DictReader(file)
            sort_choice = input(
                "How would you view your wishlist?\nmain => by sorted main/price\ncomplete => by sorted complete/price\ndefault => without sorting\nAction: "
            )
            match sort_choice:
                case "main":
                    print(table(view_main(reader)))
                case "complete":
                    print(table(view_complete(reader)))
                case "default":
                    print(table(view_default(reader)))
                case _:
                    pass
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        sys.exit("File Not Found")
    except EOFError:
        pass

#sorts list by main/price
def view_main(reader):
    for i, row in enumerate(reader):
        newlist.append(
            {
                "Name": row["name"],
                "Steam ID": row["id"],
                "Price": row["price"],
                "Main Length": row["length"],
                "Main / Price": float(row["main price ratio"]),
            }
        )
    return sorted(newlist, key=lambda row: row["Main / Price"], reverse=True)

#sorts list by complete/price
def view_complete(reader):
    for i, row in enumerate(reader):
        newlist.append(
            {
                "Name": row["name"],
                "Steam ID": row["id"],
                "Price": row["price"],
                "Complete Length": row["completionist"],
                "Complete / Price": float(row["completionist price ratio"]),
            }
        )
    return sorted(newlist, key=lambda row: row["Complete / Price"], reverse=True)

#returns list as a whole without sorting
def view_default(reader):
    for i, row in enumerate(reader):
        newlist.append(
            {
                "Name": row["name"],
                "Steam ID": row["id"],
                "Price": row["price"],
                "Main Length": row["length"],
                "Complete Length": row["completionist"],
                "Main / Price": row["main price ratio"],
                "Complete / Price": row["completionist price ratio"],
            }
        )
    return newlist

#turns list to table form using tabulate, returns tabulate(newlist)
def table(newlist):
    return (
        ("List is empty")
        if len(newlist) <1
        else tabulate(
            newlist,
            headers="keys",
            tablefmt="fancy_grid",
            showindex=range(1, len(newlist) + 1),
        )
    )

#provides options for editting previous file
def edit():
    try:
        file_name = filename()
        if filecheck(file_name) == False:
            raise FileNotFoundError("File Not Found")
    except FileNotFoundError:
        sys.exit("File Not Found")
    else:
        readtolist(file_name)
        try:
            edit_choice = input(
                "How would you update your wishlist:\nadd => adds a game to the wishlist\nremove => remove a game from the wishlist\nupdate => update the prices of your games\n"
            )
        except EOFError:
            sys.exit("Exiting Program...")
        else:
            match edit_choice:
            #adds new games to file
                case "add":
                    getandrequest()
                    writefile(file_name)
            #removes existing game from file
                case "remove":
                    for game in newlist:
                        print(game["name"])
                    try:
                        gamename = input("Game to Remove: ").title()
                    except EOFError:
                        sys.exit("Exiting Program...")
                    else:
                        if remove(gamename,newlist):
                            print(f"{gamename} succesfully removed")
                        else:
                            print(f"{gamename} not found")
                        writefile(file_name)
            #updates the price of each game in file
                case "update":
                    for game in newlist:
                        gameid = game["id"]
                        updatedprice = update(gameid)
                        game["price"] = updatedprice
                        p = re.findall(r"[0-9]+\.?[0-9]*", updatedprice.replace(",", ""))
                        p = float(*p)
                        game["main price ratio"] = float(game['length']) / float(p)
                        game["completionist price ratio"] = float(game['completionist']) / float(p)
                    writefile(file_name)

                case _:
                    pass

def remove(gamename,newlist):
    for i, row in enumerate(newlist):
        if gamename == row["name"]:
            del newlist[i]
            return True
    return False


def update(gameid):
    response = requests.get(
        "https://store.steampowered.com/api/appdetails?appids=" + gameid
    )
    o = response.json()
    return o[gameid]["data"]["price_overview"]["final_formatted"]


def main():
    while True:
        try:
            newlist.clear()
            choice = input(
                "\nWelcome to Steam Budget Wishlist\n\n"
                "Select an action:\nnew => creates a new wishlist\nview => view previously made wishlist\nedit => edit previously made wishlist\nexit => exits program\n\nAction: "
            )
        except EOFError:
            pass
        else:
            match choice:
                case "new":
                    newfile()
                case "view":
                    view()
                case "edit":
                    edit()
                case "exit":
                    sys.exit("Thank you for using Wishlist on a Budget")
                case _:
                    print("False Action\n")
        input("Press enter to continue...")

if __name__ == "__main__":
    main()