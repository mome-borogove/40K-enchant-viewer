#!/usr/bin/env python3

import re

from templates import ENCHANT_TEMPLATE

def preformat_str(s):
  '''Replace markup information in lang strings.'''
  s = re.sub(r'\[[0-9A-Fa-f]{2}([0-9A-Fa-f]{6})\]',r"<font color='#\1'>",s)
  s = re.sub(r'\[/[0-9A-Fa-f]{8}\]',r"</font>",s)
  return s

def format_item_types(item_types, item_type_map):
  return [str(item_type_map[i]) for i in item_types if i in item_type_map]

def format_item_type_map(slot_to_item_types, item_type_map):
  def format_slot_item(slot,item_types):
    s = '[ "'+str(slot)+'"'
    s+= ', '
    s+= '[' + ', '.join(['"'+s+'"' for s in format_item_types(item_types, item_type_map)]) + '] ]'
    return s
  return ',\n'.join([format_slot_item(*_) for _ in slot_to_item_types.items()])

def format_enchant_desc(enchant, slot_map):
  key = enchant.desc
  if key not in slot_map:
    return '(No name found) '+str(key)
  s = slot_map[enchant.desc]

  # Add numeric values to enchant description
  # {prop} => str
  # {prop,100} => str
  prop = enchant.desc_repl

  # *sigh* Neocore apparently doesn't fill in some properties, but they use
  # 'artifact_enchant' in the strings which don't have Property set correctly.
  if prop=='null' or prop=='undefined':
    prop = 'artifact_enchant'

  # Neocore assumes an implicit '+' in front of most numbers. When they don't
  # want one to show up, the string 'nembonusz' is added to the replacement
  # pattern (Hungarian for 'no bonus'). We never add '+' to anything, so
  # we remove the nembonusz where it appears.
  s = re.sub(r'{nembonusz;', r'{', s)

  # FIXME: Movement speed in specific is screwed up. It's not listed as a %,
  # but sometimes it is. But not always. Yay.
  #   movement_speed_in_green: 0.16, {movement_speed,100}
  #   movement_speed_in_exposed: 0.16, {movement_speed}
  # I have no idea how they're implementing this, but I don't seem to have the
  # right information. So here's what we're doing:
  # There are no enchants I'm aware of that give less than 1% movement speed.
  # So we're going to ignore the format string altogether for movement speed.
  # If it's less than 1, we're multiplying by 100. If not, leave it.
  if re.search(r'{movement_speed}', s):
    if enchant.range[1]<1:
      s = re.sub(r'{movement_speed}', r'{movement_speed,100}', s)

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
  s = re.sub(r'{deflect}', r'Deflect/Dodge', s)

  # {resource} really means the class-specific zeal 
  s = re.sub(r'{resource}', r'Focus/Adrenaline/Data-flux', s)

  # FIXME: Neocore released a bug in 2.3.1 where the string for an AoE effect
  # has the wrong substitution string. This should be changed when it gets
  # fixed, but hopefully I've written it defensively so it won't break if I
  # forget to do it.
  if (str.lower(enchant.name)=='aoe_damage_bonus_major' and
      re.search(r'{aoe_damage_bonus,100}',s)):
    s = re.sub(r'{aoe_damage_bonus,100}', r'{damage,100}', s)

  # Replace the actual numeric property
  # FIXME: The regex pattern '\*?' before the 100 multiplier is to fix a Neocore
  # bug in loot_quality and loot_quantity which are improperly formatted as
  # {loot_quality,*100} instead of {loot_quality,100}. We just ignore the
  # extraneous '*'. When this is fixed upstream, this can be removed.
  if re.search(r'{'+prop,s):
    decimal_places = 2
    # We want to collapse ranges that are identical. But it's floating point.
    if round(enchant.range[0],4)==round(enchant.range[1],4):
      # Single value
      s = re.sub(r'\{'+prop+r'\}',
                 str(round(enchant.range[0],decimal_places)), s)
      s = re.sub(r'\{'+prop+r',\*?100\}',
                 str(round(100*enchant.range[0],decimal_places))+'%', s)
    else: 
      # Range of values
      s = re.sub(r'\{'+prop+r'\}',
                 str(round(enchant.range[0],decimal_places))+' to '+str(round(enchant.range[1],decimal_places)),
                 s)  
      s = re.sub(r'\{'+prop+r',\*?100\}',
                 str(round(100*enchant.range[0],decimal_places))+'% to '+str(round(100*enchant.range[1],decimal_places))+'%',
                 s)  

  if '{' in s or '}' in s:
    print('WARNING: Unsubstituted value in string:',s)

  return s


def format_enchant(enchant, s_map):
  desc_fmt = format_enchant_desc(enchant, s_map)
  items = ','.join(["'"+str(item)+"'" for item in enchant.items])
  slots = ','.join(["'"+str(slot)+"'" for slot in enchant.slots])
  groups = ','.join(["'"+str(group)+"'" for group in enchant.groups])
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
    groups=groups)
  return s

