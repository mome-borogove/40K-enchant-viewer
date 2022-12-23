#!/usr/bin/env python3

from xml.etree import ElementTree as ETree


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
  item_types = artifacts.find('Items')
  item_type_map = {}
  for item_type in item_types:
    # Neocore is anything but consistent in their XML. Originally, we looked
    # in the 'Types' section, but the Battle Sister update screwed that up.
    # Instead, all the combo items are named identically, so we have to look in
    # 'Items'. Except *that* has bugs where some items only have an 'eng' tag
    # and not a 'Name' tag above it. So we have to do this hacky garbage.
    name_element = item_type.find('Name')
    if name_element is None:
      # ...really?
      name_element = item_type.find('name')
    if name_element is None:
      eng_element = item_type.find('eng')
    else:
      eng_element = name_element.find('eng')
    if eng_element is None:
      print('Warning: item type',str(item_type.tag),'has no name or text. If this is not an equippable item, it can be ignored.')
    else:
      name_string = eng_element.text
    item_type_map[str.lower(item_type.tag)] = name_string

  return ench_str_map, item_type_map

if __name__=='__main__':
  with open('Lang_Artifacts.xml') as f:
    string_map = parse_langs(f)
    print(str(len(string_map))+' strings mapped')
    for k in ['critical_hit_chance','critical_damage_bonus','blessed_weapon_damage_against_demons']:
      print(k,string_map[k])
