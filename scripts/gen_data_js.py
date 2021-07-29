#!/usr/bin/env python3

import re
import sys

from lib40k import parse_enchants, parse_inventory, SLOTS
# <REFACTOR> Remove the below; they should be internal to lib40k
from lib40k import parse_langs, Enchant, preformat_str, format_item_types, format_item_type_map

from slots import all_items, construct_slot_map, expand_items, items_from_slots, slots_from_items, filter_shortcuts
from emit_js import emit_js


def main(version_file, enchant_file, lang_file, inventory_file, output_file):
  with open(version_file) as f:
    version = f.read().strip()
  with open(enchant_file) as f:
    shortcuts,enchants = parse_enchants(f)
  with open(lang_file) as f:
    ench_str_map,item_type_map = parse_langs(f)
  with open(inventory_file) as f:
    relic_items, archeo_items, puritan_items, radical_items = parse_inventory(f)

  print(len(enchants),'enchants inloaded')
  print(len(ench_str_map),'strings inloaded')
  print(len(relic_items),'relic items inloaded')
  print(len(archeo_items),'archeo items inloaded')
  print(len(puritan_items),'puritan items inloaded')
  print(len(radical_items),'radical items inloaded')

  # Filter out some item types (i.e., TA construct items)
  shortcuts = filter_shortcuts(shortcuts)

  # <REFACTOR> Replace this with pre-formatted enchant data
  ench_str_map = {k:preformat_str(v) for k,v in ench_str_map.items()}

  slot_map = construct_slot_map(shortcuts)

  # Relic and morality enchants are invalid in enchantments.cfg. Instead, we
  # have to reconstruct them from the individual items in inventoryitems.cfg.
  for enchant in enchants:
    if enchant.quality=='godlike' or enchant.quality=='morality':
      enchant.shortcuts = [] # First, blow away all false maps

  # Note: once we start dealing with items, we start splitting morality into
  # two new, fake qualities: puritan and radical. See parse_inventory for
  # more info.

  # Create empty type maps for relic, archeo, puritan, and radical items
  # These map enchant names to a list of types scraped from inventoryitems.cfg.
  relic_typemap, archeo_typemap, puritan_typemap, radical_typemap = {},{},{},{}
  for map,items in [(relic_typemap,relic_items),
                   (archeo_typemap,archeo_items),
                   (puritan_typemap,puritan_items),
                   (radical_typemap,radical_items)]:
    for item in items:
      for enchant in item['enchants']:
        if enchant not in map:
          map[enchant] = []
        t = item['Type']
        # Thanks to PsyHo_GK for reporting this bug
        if t not in map[enchant]:
          map[enchant].append(t)
  print('relic map:',len(relic_typemap),'enchant types')
  print('archeo map:',len(archeo_typemap),'enchant types')
  print('puritan map:',len(puritan_typemap),'puritan types')
  print('radical map:',len(radical_typemap),'radical types')

  # Now try to unify enchants from across all rarities.
  # FIXME: Currently, seasonal tags from archeotech items are ignored.
  #   This means that if the corresponding enchant in the enchantments.cfg
  #   file does not have the correct seasonal tag, the item won't show up
  #   as seasonal. Neocore was bad at this in season 1, but season 2 and 3
  #   have more or less corrected the issue. Since season 1 is unplayable
  #   now, this is less of an issue.
  new_enchants = []
  for enchant in enchants:
    if enchant.quality=='godlike':
      if enchant.name in relic_typemap:
        enchant.items = relic_typemap[enchant.name]
        enchant.quality = 'relic'
        new_enchants.append(enchant)
      if enchant.name in archeo_typemap:
        # We create a whole separate enchant for archeotech enchants,
        # otherwise we can't distinguish between relic and archeo enchants.
        e = Enchant.copy(enchant)
        e.items = archeo_typemap[enchant.name]
        e.quality = 'archeo'
        new_enchants.append(e)
      if enchant.name not in relic_typemap and enchant.name not in archeo_typemap:
        # Enchants that are ancient-only or simply left unused in the game
        # appear here.
        enchant.items = []
        print('Warning: ignoring unused enchant '+str(enchant.name))
    # Note that we check for the 'morality' type because the enchants are
    # originally coming from enchantments.cfg, which doesn't split.
    elif enchant.quality=='morality':
      if enchant.name in puritan_typemap:
        enchant.items = puritan_typemap[enchant.name]
        # Now we replace it with the appropriate type.
        # This is safe because an enchant cannot be morality and something else,
        # nor both puritan and radical.
        enchant.quality = 'puritan'
        new_enchants.append(enchant)
      elif enchant.name in radical_typemap:
        enchant.items = radical_typemap[enchant.name]
        # Now we replace it with the appropriate type.
        # This is safe because an enchant cannot be morality and something else,
        # nor both puritan and radical.
        enchant.quality = 'radical'
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

  slot_to_item_types = {s:items_from_slots([s], slot_map, shortcuts) for s in SLOTS}
  item_type_strings = format_item_type_map(slot_to_item_types, item_type_map)

  emit_js(output_file, enchants, ench_str_map, slot_to_item_types, item_type_strings, version)

if __name__=='__main__':
  if len(sys.argv)<5:
    print('Usage: '+str(sys.argv[0])+' <version_file> <enchantments.cfg file> <Lang_Artifacts.xml file> <inventoryitems.cfg file> <output file>')
    sys.exit(-1)
  main(*sys.argv[1:])
