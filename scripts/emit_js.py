#!/usr/bin/env python3

from lib40k import format_enchant_desc, SLOTS

################################################################################

DATA_TEMPLATE='''
var __version__ = "{version}";

var SLOTS = [
{slots}
];

var RECT_SLOTS = [
  "main_implant",
  "body",
  "inoculator",
  "weapon",
  "offhand",
];

// Object constructor
function Enchant(name, str, items, slots, quality, doubled, groups, seasons) {{
  this.name = name;
  this.str = str;
  this.items = items;
  this.slots = slots;
  this.quality = quality;
  this.doubled = doubled;
  this.groups = groups;
  this.seasons = seasons;
}}

var enchants = [
{enchants}
];

var slot_items = new Map([
{item_types}
]);

'''

def format_js_data_file(enchants, ench_str_map, slot_to_item_types, item_type_strings, version):
  enchant_data = ''
  for enchant in enchants:
    enchant_data += format_enchant(enchant, ench_str_map)

  # format each slot for javascript
  slot_strings = '\n'.join(['  "'+s+'",' for s in SLOTS])

  # create the slot->item types javascript map
  # <REFACTOR> Compute this in gen_data
  #slot_to_item_types = {s:items_from_slots([s], slot_map, shortcuts) for s in SLOTS}
  # <REFACTOR> Compute this in gen_data
  #item_type_strings = format_item_type_map(slot_to_item_types, item_type_map)

  return DATA_TEMPLATE.format(
           version=version,
           enchants=enchant_data,
           slots=slot_strings,
           item_types=item_type_strings)

def emit_js(output_file, *args, **kwargs):
  with open(output_file,'w') as f:
    f.write(format_js_data_file(*args, **kwargs))
  
################################################################################

ENCHANT_TEMPLATE='''new Enchant('{name}',
              "{desc}",
              [{items}],
              [{slots}],
              '{quality}',
              {doubled},
              [{groups}],
              [{seasons}]),
'''

def format_enchant(enchant, s_map):
  # <REFACTOR> Replace this with pre-formatted enchant data
  desc_fmt = format_enchant_desc(enchant, s_map)

  items = ','.join(["'"+str(item)+"'" for item in enchant.items])
  slots = ','.join(["'"+str(slot)+"'" for slot in enchant.slots])
  groups = ','.join(["'"+str(group)+"'" for group in enchant.groups])
  seasons = ','.join([str(season) for season in enchant.seasons])
  if enchant.doubled:
    doubled = 'true'
  else:
    doubled = 'false';

  s = ENCHANT_TEMPLATE.format(
    name=enchant.name,
    desc=desc_fmt,
    items=items,
    slots=slots,
    quality=enchant.quality,
    doubled=doubled,
    groups=groups,
    seasons=seasons)
  return s

