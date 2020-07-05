#!/usr/bin/env python3

import re
import sys

from slots import SLOTS, all_items, construct_slot_map, expand_items, items_from_slots, slots_from_items, filter_shortcuts
from format_strings import preformat_str, format_enchant_desc, format_enchant, format_item_types, format_item_type_map
from templates import DATA_TEMPLATE
from parse_enchants import parse_enchants
from parse_langs import parse_langs



def main(enchant_file, lang_file, output_file):
  with open(enchant_file) as f:
    shortcuts,enchants = parse_enchants(f)
  with open(lang_file) as f:
    ench_str_map,item_type_map = parse_langs(f)

  # Filter out some item types (i.e., TA construct items)
  shortcuts = filter_shortcuts(shortcuts)

  print(len(enchants),'enchants inloaded')
  print(len(ench_str_map),'strings inloaded')

  ench_str_map = {k:preformat_str(v) for k,v in ench_str_map.items()}
  slot_map = construct_slot_map(shortcuts)
  for enchant in enchants:
    enchant.items = expand_items(enchant.shortcuts, shortcuts)
    enchant.slots = slots_from_items(enchant.items, slot_map)
    enchant.items = format_item_types(enchant.items, item_type_map)

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
              enchants=enchant_data,
              slots=slot_strings,
              item_types=item_type_strings))


if __name__=='__main__':
  if len(sys.argv)<3:
    print('Usage: '+str(sys.argv[0])+' <enchantments.cfg file> <Lang_Artifacts.xml file> <output file>')
    sys.exit(-1)
  main(*sys.argv[1:4])
