#!/usr/bin/env python3

from xml.etree import ElementTree as ETree


def parse_langs(file):
  root = ETree.parse(file)
  artifacts = root.find('Artifacts')
  enchants = artifacts.find('Enchantment')
  smap = {}
  for ench in enchants:
    if str.lower(ench.tag) in enchants:
      print('AARGH!',ench.tag)
    smap[str.lower(ench.tag)] = ench.find('desc').find('eng').text
  return smap

if __name__=='__main__':
  with open('Lang_Artifacts.xml') as f:
    string_map = parse_langs(f)
    print(str(len(string_map))+' strings mapped')
    for k in ['critical_hit_chance','critical_damage_bonus','blessed_weapon_damage_against_demons']:
      print(k,string_map[k])

    #for k,v in string_map.items():
    #  if v.count('{')>1:
    #    print(k,v)
