# Python Script that filters JSON file from https://db.ygoprodeck.com/api/v7/cardinfo.php database
#       and creates CSV that can be imported into Google Sheets
# https://pastebin.com/aMKM2sqg
#       make sure to import as TAB delimited!
#       showing just the card name and its tcgplayer.com market price
#           sorted from highest price to lowest (descending order)
#       and grouped by border, Monster Spell Trap Extra

import json  # https://docs.python.org/3/library/json.html
import enum
import csv
from datetime import datetime

# make dictionary from json file API query result
with open("cardinfo.php.json", encoding='utf-8') as input_file:
    cards_in_set = json.load(input_file)
# print(type(cards_in_set))
# print(json.dumps(cards_in_set, indent=4)) # pretty print

SETNAME = "Maximum Gold"

cards = cards_in_set['data']

main_name_price_dict = {}  # first elem 0
spell_name_price_dict = {}  # 1
trap_name_price_dict = {}  # 2
extra_name_price_dict = {}  # 3


class CardBorders(enum.Enum):
    Monster = 0
    Spell = 1
    Trap = 2
    Extra = 3


name_price_dict_list = [main_name_price_dict, spell_name_price_dict,
                        trap_name_price_dict, extra_name_price_dict]

for x in range(len(cards)):
    if "Spell" in cards[x]['type']:
        index_type = CardBorders.Spell.value
    elif "Trap" in cards[x]['type']:
        index_type = CardBorders.Trap.value
    elif ("Link" or "Fusion" or "Token" or "Synchro" or "XYZ") in cards[x]['type']:
        index_type = CardBorders.Extra.value
    else:
        index_type = CardBorders.Monster.value

    # appears to use 30 day average from tcgplayer as set_price with a one week lag??? Just know it is about 5-10% jitter usually above market price

    # Insert TCG Player price for all cards with this ID AKA all legal versions of this card from ANY SET
    # name_price_dict_list[index_type][cards[x]['name']] = cards[x]['card_prices'][0]['tcgplayer_price']

    set_price_of_card = 0.00666

    for setts in cards[x]['card_sets']:
        if setts['set_name'] == SETNAME:
            set_price_of_card = float(setts['set_price'])

    if set_price_of_card == 0.00666:
        print("API corrupted or SETNAME " + SETNAME + " incorrect")

    # build list of dictionaries containing spells traps monsters key=name value=price
    name_price_dict_list[index_type][cards[x]['name']] = set_price_of_card

# probably better way to do this with list comprehension somehow
# ex_info = [x for x in cards]

# sort by price descending
for x in range(len(name_price_dict_list)):
    price_desc = dict(sorted(((value, key) for (key, value) in name_price_dict_list[x].items()), reverse=True))
    #  make keys (prices) the values
    price_desc = {value: key for key, value in price_desc.items()}
    # overwrite alphabetically sorted dictionarys
    name_price_dict_list[x] = price_desc


# write csv file that will be accepted by google sheets

csv_out = SETNAME + str(datetime.now().date()) + ".csv"
try:
    with open(csv_out, 'w', newline='') as csvfile:
        w = csv.writer(csvfile, delimiter='\t')
        w.writerow(["Name", "Price $USD"])
        # w.writerow(["MONSTERS", SETNAME]) # could do this but naw
        for index in range(len(name_price_dict_list)):
            w.writerows(name_price_dict_list[index].items())



except IOError:
    print("I/O Error")
