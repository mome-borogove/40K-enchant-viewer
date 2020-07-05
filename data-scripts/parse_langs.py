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
  item_types = artifacts.find('Types')
  item_type_map = {}
  for item_type in item_types:
    item_type_map[str.lower(item_type.tag)] = item_type.find('eng').text

  return ench_str_map, item_type_map

if __name__=='__main__':
  with open('Lang_Artifacts.xml') as f:
    string_map = parse_langs(f)
    print(str(len(string_map))+' strings mapped')
    for k in ['critical_hit_chance','critical_damage_bonus','blessed_weapon_damage_against_demons']:
      print(k,string_map[k])
