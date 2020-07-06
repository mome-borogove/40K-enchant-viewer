#!/usr/bin/env python3

import re
import sys

from slots import SLOTS, all_items, construct_slot_map, expand_items, items_from_slots, slots_from_items, filter_shortcuts
from format_strings import preformat_str, format_enchant_desc, format_enchant, format_item_types, format_item_type_map
from templates import DATA_TEMPLATE
from parse_enchants import parse_enchants
from parse_langs import parse_langs
from parse_inventory import parse_inventory

def main(version_file, enchant_file, lang_file, inventory_file, output_file):
  with open(version_file) as f:
    version = f.read().strip()
  with open(enchant_file) as f:
    shortcuts,enchants = parse_enchants(f)
  with open(lang_file) as f:
    ench_str_map,item_type_map = parse_langs(f)
  with open(inventory_file) as f:
    relic_items, morality_items = parse_inventory(f)

  print(len(enchants),'enchants inloaded')
  print(len(ench_str_map),'strings inloaded')
  print(len(relic_items),'relic items inloaded')
  print(len(morality_items),'morality items inloaded')

  # Filter out some item types (i.e., TA construct items)
  shortcuts = filter_shortcuts(shortcuts)

  ench_str_map = {k:preformat_str(v) for k,v in ench_str_map.items()}
  slot_map = construct_slot_map(shortcuts)

  # Relic and morality enchants are invalid in enchantments.cfg. Instead, we
  # have to reconstruct them from the individual items in inventoryitems.cfg.
  for enchant in enchants:
    if enchant.quality=='relic' or enchant.quality=='morality':
      enchant.shortcuts = [] # First, blow away all false maps
  # Create an enchant map for relic and morality items
  special_enchant_map = {}
  for item in relic_items+morality_items:
    for enchant in item['enchants']:
      if enchant not in special_enchant_map:
        special_enchant_map[enchant] = []
      special_enchant_map[enchant].append(item['Type'])
  
  for enchant in enchants:
    if enchant.quality=='relic' or enchant.quality=='morality':
      if enchant.name in special_enchant_map:
        enchant.items = special_enchant_map[enchant.name]
        if enchant.quality=='morality':
          print(enchant)
      else:
        # Neocore doesn't distinguish between 'godlike' and 'biggodlike'
        # enchants in enchantments.cfg, but they *do* distinguish items
        # in inventoryitems.cfg, so some 'godlike' enchants only appear
        # on 'biggodlike' items.
        enchant.items = []
        print('Warning: ignoring unused enchant '+str(enchant.name))
    elif enchant.quality=='primary' or enchant.quality=='secondary':
      enchant.items = expand_items(enchant.shortcuts, shortcuts)
    else:
      enchant.items = []
    enchant.slots = slots_from_items(enchant.items, slot_map)
    enchant.items = format_item_types(enchant.items, item_type_map)

  # Filter out enchants that no longer have any valid item types. These will
  # just confuse people. (They do exist, but just on archeo or ancient items)
  enchants = [_ for _ in enchants if len(_.items)>0]

  enchant_data = ''
  for enchant in enchants:
    enchant_data += format_enchant(enchant, ench_str_map)

  # format each slot for javascript
  slot_strings = '\n'.join(["  Slot('{0}'),".format(s) for s in SLOTS])

  # create the slot->item types javascript map
  slot_to_item_types = {s:items_from_slots([s], slot_map, shortcuts) for s in SLOTS}
  item_type_strings = format_item_type_map(slot_to_item_types, item_type_map)

  with open(output_file,'w') as f:
    f.write(DATA_TEMPLATE.format(
              version=version,
              enchants=enchant_data,
              slots=slot_strings,
              item_types=item_type_strings))


if __name__=='__main__':
  if len(sys.argv)<5:
    print('Usage: '+str(sys.argv[0])+' <version_file> <enchantments.cfg file> <Lang_Artifacts.xml file> <inventoryitems.cfg file> <output file>')
    sys.exit(-1)
  main(*sys.argv[1:])
