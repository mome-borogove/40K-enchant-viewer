#!/usr/bin/env python3

SLOTS=[
  'neural_implant', 'eye_implant', 'main_implant', 'purity_seal', 'belt',
  'body', 'inoculator', 'weapon', 'signum', 'offhand', 'construct'
]

### FIXME: 'inoculator_start'
# So I'm not entirely sure what this item represents, but I suspect it is the
# inoculator you are given the first time you unlock it. In every data file I
# have seen it, it is identical or a subset of the inoculator.
# In any case, I'm basically ignoring its existence. Everywhere it appears, I
# try to remove it. If that turns out to be wrong, let's fix that.
#
# Note: This item does not appear in Neocore's item shortcut list, not even
# in the 'all_item' shortcut. Apparently they don't like it either.


def filter_shortcuts(shortcuts):
  new_shortcuts = {}
  for k,v in shortcuts.items():
    # Filter out all references to construct enchants
    new_v = [_ for _ in v if 'techadeptsummon' not in _]
    new_shortcuts[k] = new_v
  return new_shortcuts

def all_items(shortcuts):
  return list(set(shortcuts['all_item']))


def construct_slot_map(shortcuts):
  '''Maps item types (lasgun) and shortcuts (weapon_2h) to a basic item slot types (weapon).'''
  # Signums count as one slot.
  # 'construct' encompasses all tech-adept construct gear

  # This is a bit of a manual process...

  slot_map = {}
  # Fill out the 1:1 slots
  for slot in ['neural_implant','eye_implant','main_implant','purity_seal',
               'inoculator','signum']:
    slot_map[slot] = slot
  # Defensively map this to a known slot
  slot_map['inoculator_start'] = 'inoculator'
  # *sigh* construct gear doesn't have a shortcut, so we guess by name hints
  for item in shortcuts['all_item']:
    if 'techadeptsummon' in item:
      slot_map[item] = 'construct'
  # Now for the N:1 slots...
  def map_all_to(shortcut, slot):
    for item in shortcuts[shortcut]:
      slot_map[item] = slot
    slot_map[shortcut] = slot
  map_all_to('belts', 'belt')
  map_all_to('shields', 'offhand')
  map_all_to('armors','body')
  for k in shortcuts.keys():
    if 'weapon_' in k:
      map_all_to(k, 'weapon')

  return slot_map

def items_from_slots(slots, slot_map, shortcuts):
  '''Compute the item types which can fit in a slot.'''
  return [item_type for item_type in all_items(shortcuts) if slot_map[item_type] in slots]

def slots_from_items(items, slot_map):
  '''Compute the set of slots occupied by a set of item types'''

  # Expand item shortcuts and unique-ify slots
  unique_slots = set()
  for item in items:
    if item not in slot_map:
      print('Warning: missing a slot map for '+str(item))
    else:
      unique_slots.add(slot_map[item])
  return sorted(list(unique_slots))


def expand_items(slot_list, shortcuts):
  '''Expands the shortcuts in a list to specific item types.'''

  # Pretend 'inoculator_start' doesn't exist
  slot_list = [_ for _ in slot_list if _!='inoculator_start']

  unique_items = set()
  for item_or_shortcut in slot_list:
    if item_or_shortcut in shortcuts:
      unique_items |= set(shortcuts[item_or_shortcut])
    elif item_or_shortcut in all_items(shortcuts):
      unique_items |= set([item_or_shortcut])
    #else:
    #  print('Warning: Invalid slot or shortcut name: "'+str(item_or_shortcut)+'"')
  return sorted(list(unique_items))
