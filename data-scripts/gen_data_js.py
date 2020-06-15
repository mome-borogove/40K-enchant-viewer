#!/usr/bin/env python3

import re
import sys

from parse_enchants import parse_enchants
from parse_langs import parse_langs

def preformat_str(s):
  '''Replace markup information in lang strings.'''
  #s = re.sub(r'\[[0-9A-Fa-f]{2}([0-9A-Fa-f]{6})\]',r"<font color='#\1'>",s)
  #s = re.sub(r'\[/[0-9A-Fa-f]{8}\]',r"</font>",s)
  #FIXME: NYI, just delete them
  s = re.sub(r'\[[0-9A-Fa-f]{8}\]',r'',s)
  s = re.sub(r'\[/[0-9A-Fa-f]{8}\]',r'',s)
  return s

def construct_slot_map(items):
  return {} # { shortcut : [slot, ...], ... }

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

def expand_slots(enchant, slot_map):
  # expand shortcuts and unique-ify slots
  return enchant

def format_enchant_desc(enchant, s_map):
  key = enchant.desc
  if key not in s_map:
    return "<div class='error'>Enchant description missing</div>"
  s = s_map[enchant.desc]
  # Add numeric values to enchant description
  # {prop} => str
  # {prop,100} => str
  prop = enchant.desc_repl
  # *sigh* Neocore apparently doesn't fill in some properties, but they use
  # 'artifact_enchant' in the strings which don't have Property set correctly.
  if prop=='null' or prop=='undefined':
    prop = 'artifact_enchant'
  if re.search(r'{'+prop,s):
    if enchant.range[0]==enchant.range[1]:
      s = re.sub(r'\{'+prop+r'\}', str(enchant.range[0]), s)
      s = re.sub(r'\{'+prop+r',100\}', str(enchant.range[0])+'%', s)
    else:
      s = re.sub(r'\{'+prop+r'\}',
                 str(enchant.range[0])+' to '+str(enchant.range[1]),
                 s)
      s = re.sub(r'\{'+prop+r',100\}',
                 str(100*enchant.range[0])+'% to '+str(100*enchant.range[1])+'%',
                 s)
  
  # FIXME: substitute numerics
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
  Slot('body_armour'),
  Slot('inoculator'),
  Slot('weapon1'),
  Slot('signum1'),
  Slot('signum2'),
  Slot('weapon2')
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
  enchants = [expand_slots(ench,slot_map) for ench in enchants]

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
