#!/usr/bin/env python3

import re
import sys

from parse_enchants import parse_enchants
from parse_langs import parse_langs

SLOTS=[
  'neural_implant','eye_implant','main_implant','purity_seal', 'belt', 'body',
  'inoculator','weapon','signum','offhand',
]

def preformat_str(s):
  '''Replace markup information in lang strings.'''
  #s = re.sub(r'\[[0-9A-Fa-f]{2}([0-9A-Fa-f]{6})\]',r"<font color='#\1'>",s)
  #s = re.sub(r'\[/[0-9A-Fa-f]{8}\]',r"</font>",s)
  #FIXME: NYI, just delete them
  s = re.sub(r'\[[0-9A-Fa-f]{8}\]',r'',s)
  s = re.sub(r'\[/[0-9A-Fa-f]{8}\]',r'',s)
  return s

def construct_slot_map(items):
  # A "slot map" maps specific items and their group-shortcuts to one of the
  # 10 basic slots. (signums count as one "slot")
  #   { 'lasgun' => 'weapon1',
  #     'weapon_1h_ammo' => 'weapon1',
  #     'shields' => 'belt'
  # This is a bit of a manual process...
  slot_map = {}
  # Fill out the 1:1 slots
  for slot in ['neural_implant','eye_implant','main_implant','purity_seal',
               'inoculator','signum','construct']:
    slot_map[slot] = [slot]
  # Still don't know what this one is
  slot_map['inoculator_start'] = ['inoculator']
  # *sigh* construct gear doesn't have a shortcut...
  for item in items['all_item']:
    if 'techadeptsummon' in item:
      slot_map[item] = ['construct']
  # Now for the N:1 slots...
  def map_all_to(shortcut, slot):
    for item in items[shortcut]:
      slot_map[item] = [slot]
    slot_map[shortcut] = [slot]
  map_all_to('belts', 'belt')
  map_all_to('shields', 'offhand')
  map_all_to('armors','body')
  for k in items.keys():
    if 'weapon_' in k:
      map_all_to(k, 'weapon')
  # Now the 1:N slots...
  slot_map['all_item'] = [_ for _ in SLOTS]

  for k in items.keys():
    assert k in slot_map, k+' not mapped'  

  return slot_map

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

def fix_slots(enchant, slot_map):
  '''Slots specified by config files use shortcuts and can be wrong. Fix them.'''

  # Expand item shortcuts and unique-ify slots
  unique_slots = set()
  for item in enchant.slots:
    if item not in slot_map:
      print('Warning: Enchant '+str(enchant.name)+' is missing a slot map for '+str(item)+'\n'+str(enchant))
    else:
      unique_slots.update(slot_map[item])
  enchant.slots = sorted(list(unique_slots))
  return enchant

def format_enchant_desc(enchant, s_map):
  key = enchant.desc
  if key not in s_map:
    return '(No name found:) '+str(key)
  s = s_map[enchant.desc]
  # Add numeric values to enchant description
  # {prop} => str
  # {prop,100} => str
  prop = enchant.desc_repl
  # *sigh* Neocore apparently doesn't fill in some properties, but they use
  # 'artifact_enchant' in the strings which don't have Property set correctly.
  if prop=='null' or prop=='undefined':
    prop = 'artifact_enchant'

  # FIXME: Movement speed in specific is screwed up. It's not listed as a %, but 
  # sometimes it is. But not always. Yay.
  # So if the string is {movement_speed}, it's actually a broken % value
  # If it's {movement_speed,100}, it's a normal not-broken % value

  # Replace the actual numeric property
  if re.search(r'{'+prop,s):
    decimal_places = 2
    if round(enchant.range[0],4)==round(enchant.range[1],4): # yay floating point
      s = re.sub(r'\{'+prop+r'\}',
                 str(round(enchant.range[0],decimal_places)), s)
      s = re.sub(r'\{'+prop+r',100\}',
                 str(round(100*enchant.range[0],decimal_places))+'%', s)
    else:
      s = re.sub(r'\{'+prop+r'\}',
                 str(round(enchant.range[0],decimal_places))+' to '+str(round(enchant.range[1],decimal_places)),
                 s)
      s = re.sub(r'\{'+prop+r',100\}',
                 str(round(100*enchant.range[0],decimal_places))+'% to '+str(round(100*enchant.range[1],decimal_places))+'%',
                 s)
  # FIXME: abilities are indexed improperly. Lang entry is listed as:
  # "{ability_X} {ability}" but the enchant property is {ability_X}, so when
  # we substitute, we're left with an ambiguous {ability}.
  return s

def format_enchant(enchant, s_map):
  ENCHANT_TEMPLATE='''new Enchant('{name}',
              "{desc}",
              [{slots}],
              '{quality}',
              [{groups}]),
  '''

  desc_fmt = format_enchant_desc(enchant, s_map)
  slots = ','.join(["'"+str(slot)+"'" for slot in enchant.slots])
  groups = ','.join(["'"+str(group)+"'" for group in enchant.groups])

  s = ENCHANT_TEMPLATE.format(
    name=enchant.name,
    desc=desc_fmt,
    slots=slots,
    quality=enchant.quality,
    groups=groups)
  return s

DATA_TEMPLATE='''
function Slot(name) {{
  this.name = name
}}

var slots = [
  Slot('neural_implant'),
  Slot('eye_implant'),
  Slot('main_implant'),
  Slot('purity_seal'),
  Slot('belt'),
  Slot('body'),
  Slot('inoculator'),
  Slot('weapon'),
  Slot('signum'),
  Slot('offhand')
];

// Object constructor
function Enchant(name, str, slots, quality, groups, range) {{
  this.name = name;
  this.str = str;
  this.slots = slots;
  this.quality = quality;
  this.groups = groups;
  this.range = range;
}}

var enchants = [
{enchants}
];

var enchant_groups = new Map();
{enchant_groups}
'''


def main(enchant_file, lang_file, output_file):
  with open(enchant_file) as f:
    items,enchants = parse_enchants(f)
  with open(lang_file) as f:
    s_map = parse_langs(f)

  print(len(enchants),'items inloaded')
  print(len(s_map),'strings inloaded')

  s_map = {k:preformat_str(v) for k,v in s_map.items()}
  slot_map = construct_slot_map(items)
  enchants = [fix_slots(ench,slot_map) for ench in enchants]

  enchant_data = ''
  for enchant in enchants:
    enchant_data += format_enchant(enchant, s_map)

  group_map = construct_group_map(items)
  group_map_data = format_group_map(group_map)

  with open(output_file,'w') as f:
    f.write(DATA_TEMPLATE.format(
              enchants=enchant_data,
              enchant_groups=group_map_data))


if __name__=='__main__':
  if len(sys.argv)<3:
    print('Usage: '+str(sys.argv[0])+' <enchantments.cfg file> <Lang_Artifacts.xml file> <output file>')
    sys.exit(-1)
  main(*sys.argv[1:4])
