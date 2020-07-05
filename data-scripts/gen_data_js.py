#!/usr/bin/env python3

import re
import sys

from slots import SLOTS, construct_slot_map, expand_items, fill_slots
from format_strings import preformat_str, format_enchant_desc
from templates import DATA_TEMPLATE, ENCHANT_TEMPLATE
from parse_enchants import parse_enchants
from parse_langs import parse_langs


def construct_group_map(enchants):
  return {} # { group : [ench, ...], ... }

def format_group_map(group_map):
  GROUP_TEMPLATE = '''
  enchant_groups.set('{group}',[{enchants}]);
  '''
  s = ''
  for group,enchants in group_map.items():
    s += GROUP_TEMPLATE.format(group=group, enchants=enchants)
  return s

def format_enchant(enchant, s_map):
  desc_fmt = format_enchant_desc(enchant, s_map)
  items = ','.join(["'"+str(item)+"'" for item in enchant.items])
  slots = ','.join(["'"+str(slot)+"'" for slot in enchant.slots])
  groups = ','.join(["'"+str(group)+"'" for group in enchant.groups])

  s = ENCHANT_TEMPLATE.format(
    name=enchant.name,
    desc=desc_fmt,
    items=items,
    slots=slots,
    quality=enchant.quality,
    groups=groups)
  return s


def main(enchant_file, lang_file, output_file):
  with open(enchant_file) as f:
    shortcuts,enchants = parse_enchants(f)
  with open(lang_file) as f:
    s_map = parse_langs(f)

  print(len(enchants),'enchants inloaded')
  print(len(s_map),'strings inloaded')

  s_map = {k:preformat_str(v) for k,v in s_map.items()}
  slot_map = construct_slot_map(shortcuts)
  for enchant in enchants:
    enchant.items = expand_items(enchant.shortcuts, shortcuts)
    enchant.slots = fill_slots(enchant.items, slot_map)
  

  enchant_data = ''
  for enchant in enchants:
    enchant_data += format_enchant(enchant, s_map)

  group_map = construct_group_map(shortcuts)
  group_map_data = format_group_map(group_map)

  # format each slot for javascript
  slot_strings = '\n'.join(["  Slot('{0}'),".format(s) for s in SLOTS])

  with open(output_file,'w') as f:
    f.write(DATA_TEMPLATE.format(
              enchants=enchant_data,
              enchant_groups=group_map_data,
              slots=slot_strings))


if __name__=='__main__':
  if len(sys.argv)<3:
    print('Usage: '+str(sys.argv[0])+' <enchantments.cfg file> <Lang_Artifacts.xml file> <output file>')
    sys.exit(-1)
  main(*sys.argv[1:4])
