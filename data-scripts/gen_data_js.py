#!/usr/bin/env python3

import re
import sys

from slots import SLOTS, all_items, construct_slot_map, expand_items, items_from_slots, slots_from_items, filter_shortcuts
from format_strings import preformat_str, format_enchant_desc, format_enchant, format_item_types, format_item_type_map
from templates import DATA_TEMPLATE
from parse_enchants import parse_enchants, Enchant
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
    relic_items, archeo_items, morality_items = parse_inventory(f)

  print(len(enchants),'enchants inloaded')
  print(len(ench_str_map),'strings inloaded')
  print(len(relic_items),'relic items inloaded')
  print(len(archeo_items),'archeo items inloaded')
  print(len(morality_items),'morality items inloaded')

  # Filter out some item types (i.e., TA construct items)
  shortcuts = filter_shortcuts(shortcuts)

  ench_str_map = {k:preformat_str(v) for k,v in ench_str_map.items()}
  slot_map = construct_slot_map(shortcuts)

  # Relic and morality enchants are invalid in enchantments.cfg. Instead, we
  # have to reconstruct them from the individual items in inventoryitems.cfg.
  for enchant in enchants:
    if enchant.quality=='godlike' or enchant.quality=='morality':
      enchant.shortcuts = [] # First, blow away all false maps
  # Create enchant maps for relic, archeo, and morality items
  relic_enchant_map = {}
  archeo_enchant_map = {}
  morality_enchant_map = {}
  for map,items in [(relic_enchant_map,relic_items),
                   (archeo_enchant_map,archeo_items),
                   (morality_enchant_map,morality_items)]:
    for item in items:
      for enchant in item['enchants']:
        if enchant not in map:
          map[enchant] = []
        t = item['Type']
        # Thanks to PsyHo_GK for reporting this bug
        if t not in map[enchant]:
          map[enchant].append(t)
  print('relic map:',len(relic_enchant_map),'enchant types')
  print('archeo map:',len(archeo_enchant_map),'enchant types')
  print('morality map:',len(morality_enchant_map),'enchant types')

  new_enchants = []
  for enchant in enchants:
    if enchant.quality=='godlike':
      if enchant.name in relic_enchant_map:
        enchant.items = relic_enchant_map[enchant.name]
        enchant.quality = 'relic'
        new_enchants.append(enchant)
      if enchant.name in archeo_enchant_map:
        # We create a whole separate enchant for archeotech enchants,
        # otherwise we can't distinguish between relic and archeo enchants.
        e = Enchant.copy(enchant)
        e.items = archeo_enchant_map[enchant.name]
        e.quality = 'archeo'
        new_enchants.append(e)
      if enchant.name not in relic_enchant_map and enchant.name not in archeo_enchant_map:
        # Enchants that are ancient-only or simply left unused in the game
        # appear here.
        enchant.items = []
        print('Warning: ignoring unused enchant '+str(enchant.name))
    elif enchant.quality=='morality':
      if enchant.name in morality_enchant_map:
        enchant.items = morality_enchant_map[enchant.name]
        new_enchants.append(enchant)
      else:
        # Enchants that are ancient-only or simply left unused in the game
        # appear here.
        enchant.items = []
        print('Warning: ignoring unused enchant '+str(enchant.name))
    elif enchant.quality=='primary' or enchant.quality=='secondary':
      enchant.items = expand_items(enchant.shortcuts, shortcuts)
      new_enchants.append(enchant)
    else:
      # Enchants that are ancient-only or simply left unused in the game
      # appear here.
      enchant.items = []
      print('Warning: ignoring unused enchant '+str(enchant.name))

  # Technically, we only needed to add the new archeo ones here, but if we did
  # that, all the archeotech items appear at the bottom of the list. I kind of
  # like keeping it in Neocore-order.
  enchants = new_enchants

  for enchant in enchants:
    enchant.slots = slots_from_items(enchant.items, slot_map)
    enchant.items = format_item_types(enchant.items, item_type_map)


  # Filter out enchants that no longer have any valid item types. These will
  # just confuse people.
  enchants = [_ for _ in enchants if len(_.items)>0]

  # Also filter out enchants that cannot roll. No sense in listing them.
  enchants = [_ for _ in enchants if not _.no_roll]

  enchant_data = ''
  for enchant in enchants:
    enchant_data += format_enchant(enchant, ench_str_map)

  # format each slot for javascript
  slot_strings = '\n'.join(['  "'+s+'",' for s in SLOTS])

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
