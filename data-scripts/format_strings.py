#!/usr/bin/env python3

import re

from templates import ENCHANT_TEMPLATE

def preformat_str(s):
  '''Replace markup information in lang strings.'''
  s = re.sub(r'\[[0-9A-Fa-f]{2}([0-9A-Fa-f]{6})\]',r"<font color='#\1'>",s)
  s = re.sub(r'\[/[0-9A-Fa-f]{8}\]',r"</font>",s)
  #FIXME: NYI, just delete them
  #s = re.sub(r'\[[0-9A-Fa-f]{8}\]',r'',s)
  #s = re.sub(r'\[/[0-9A-Fa-f]{8}\]',r'',s)
  return s

def format_item_types(item_types, item_type_map):
  return [item_type_map[i] for i in item_types if i in item_type_map]

def format_item_type_map(slot_to_item_types, item_type_map):
  def format_slot_item(slot,item_types):
    s = '[ "'+str(slot)+'"'
    s+= ', '
    s+= '"' + ', '.join(format_item_types(item_types, item_type_map)) + '" ]'
    return s
  return ',\n'.join([format_slot_item(*_) for _ in slot_to_item_types.items()])

def format_enchant_desc(enchant, slot_map):
  key = enchant.desc
  if key not in slot_map:
    return '(No name found:) '+str(key)
  s = slot_map[enchant.desc]

  # Add numeric values to enchant description
  # {prop} => str
  # {prop,100} => str
  prop = enchant.desc_repl

  # *sigh* Neocore apparently doesn't fill in some properties, but they use
  # 'artifact_enchant' in the strings which don't have Property set correctly.
  if prop=='null' or prop=='undefined':
    prop = 'artifact_enchant'

  # FIXME: Movement speed in specific is screwed up. It's not listed as a %,
  # but sometimes it is. But not always. Yay.
  # So if the string is {movement_speed}, it's actually a broken % value
  # If it's {movement_speed,100}, it's a normal not-broken % value

  # Abilities are indexed improperly. The Lang entry is listed as:
  # "{ability_X} {ability}" but the enchant property is {ability_X}, so if we
  # just substitute {ability_X}, we're left with a raw, ambiguous "{ability}".
  # Instead, we pre-emptively replace {ability} with an appropriate string
  # based on the {ability_X} we found elsewhere.
  if re.search(r'{ability_offensive}', s):
    s = re.sub(r'{ability}', 'Warfare/Accuracy/Force/Logic', s)
  elif re.search(r'{ability_survival}', s):
    s = re.sub(r'{ability}', 'Toughness/Survival/Resilience/Bionics', s)
  elif re.search(r'{ability_special}', s):
    s = re.sub(r'{ability}', 'Virtue/Bloodlust/Psy Focus/Mindlink', s)

  # {deflect} really means "Deflect or Dodge"
  s = re.sub(r'{deflect}', 'Deflect/Dodge', s)

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

