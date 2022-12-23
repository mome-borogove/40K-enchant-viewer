#!/usr/bin/env python3

from xml.etree import ElementTree as ETree

# Neocore decided to give all of the Battle Sister weapons the same type name
# for some reason. Oh they have different names in the <Items> section, but
# *that* section is missing a ton of items altogether. Without a rational way
# to reconcile these two sections, I've elected to just manually override
# the duplicate names. At least we won't be missing anything.
# NOTE: I'm using raw &'s here, because these labels will be on buttons,
# which don't interpret HTML.
# FIXME: In the future, if TA construct items get added, they should get
# added here, too. They're in the same boat.
EXCEPTIONS={
  'c_blessed_blade_rod': 'Blessed Blade & Rod',
  'c_bolt_pistol_chainsword': 'Bolt Pistol & Chainsword',
  'c_chainsword_rod': 'Chainsword & Rod',
  'c_inferno_pistol_chainsword': 'Inferno Pistol & Chainsword',
  'c_plasma_pistol_blessed_blade': 'Plasma Pistol & Blessed Blade',
  'c_plasma_pistol_brazier': 'Plasma Pistol & Brazier',
  'c_hand_flamer_brazier': 'Hand Flamer & Brazier',
  'c_hand_flamer_rod': 'Hand Flamer & Rod',
  'power_halberd': 'Power Halberd',
  'power_maul': 'Power Maul',
  # Why would you do this!? Literally every other gun isn't done this way!
  'flamer': 'Flamer',
}

def parse_langs(file):
  root = ETree.parse(file)
  artifacts = root.find('Artifacts')

  # Build the enchant string map
  enchants = artifacts.find('Enchantment')
  ench_str_map = {}
  for ench in enchants:
    if str.lower(ench.tag) in enchants:
      print('Duplicate enchant string description',ench.tag)
    ench_str_map[str.lower(ench.tag)] = ench.find('desc').find('eng').text

  # Build the item type string map
  item_types = artifacts.find('Types')
  item_type_map = {}

  for item_type in item_types:
    item_type_map[str.lower(item_type.tag)] = item_type.find('eng').text

  # Manually hack-in some exceptions to fix Neocore's inconsistencies.
  for item_type in EXCEPTIONS:
    item_type_map[item_type] = EXCEPTIONS[item_type]

  # Future-proofing: Defensively check for duplicates in the item type map.
  # This will catch any more nonsense like the Battle Sister changes.
  for item_type_string in set(item_type_map.values()):
    num_strings = len([_ for _ in item_type_map.values() if _==item_type_string])
    if num_strings>1:
      affected = [_ for _ in item_type_map if item_type_map[_]==item_type_string]
      print('Warning: Duplicate item type strings found: "'+str(item_type_string)+'"')
      print('         Affected items:')
      for aff in affected:
        print('           '+str(aff))

  return ench_str_map, item_type_map

if __name__=='__main__':
  with open('Lang_Artifacts.xml') as f:
    string_map = parse_langs(f)
    print(str(len(string_map))+' strings mapped')
    for k in ['critical_hit_chance','critical_damage_bonus','blessed_weapon_damage_against_demons']:
      print(k,string_map[k])
