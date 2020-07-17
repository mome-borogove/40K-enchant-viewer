#!/usr/bin/env python3

SHOW_ALL = False

from enum import Enum
import re
import sys

from fsm import FSM
from parse_langs import parse_langs
from parse_enchants import parse_enchants

_S = Enum('_S','TOP ENTRY_START ENTRY INNER')

def store_name(M,D):
  D['current_item'] = { 'name': str.lower(M[0]) }
  return _S.ENTRY_START

def store_value(M,D):
  D['current_item'][M[0]] = M[1]
  return None

def commit_item(M,D):
  item = D['current_item']
  # Filter out all non-item entries
  if (('quality' in item) and ('Type' in item) and (item['Type']!='blueprint')):
    # Keep relic enchants
    if (('godlike' in item['quality']) and ('enchants' in item)):
      D['relic'].append(item)
    elif (('biggodlike' in item['quality']) and ('enchants' in item)):
      D['archeo'].append(item)
    elif (('morality' in item['quality']) and ('enchants' in item)):
      D['morality'].append(item)
  # default: drop the entry
  D['current_item'] = {}
  return _S.TOP 

def store_quality(M,D):
  D['current_item']['quality'] = M[0].split(',')

def store_enchants(M,D):
  D['current_item']['enchants'] = [str.lower(e) for e in M[0].split(',')]

machine = {
  _S.TOP: [
    (r'([^\s]+)', store_name),
    (r' *', None),
  ],
  _S.ENTRY_START: [
    (r'{', lambda: _S.ENTRY ),
  ],
  _S.ENTRY: [
    (r'{', lambda: _S.INNER ),
    (r'}', commit_item),
    (r'(Type)=(.*)', store_value),
    (r'Rarity=(.*)', store_quality),
    (r'MainEnchant=(.*)', store_enchants),
    (r'GodlikeEnchants=(.*)', store_enchants),
    (r'(.*)=(.*)', None),
    (r'', None),
  ],
  _S.INNER: [
    (r'}', lambda: _S.ENTRY),
    (r'.*', None),
  ],
}

def parse_inventory(file):
  fsm = FSM(_S, _S.TOP, [_S.TOP], machine)
  fsm.reset()
  fsm.data = {'current_item': {}, 'relic': [], 'morality': [], 'archeo': []}
  #fsm.tracing(True)

  fsm.parse(file)
  return fsm.data['relic'], fsm.data['archeo'], fsm.data['morality']


if __name__=='__main__':

  with open('inventoryitems.cfg') as f:
    relic, morality = parse_inventory(f)
    print(str(len(relic)),'relic items mapped')
    print(str(len(morality)),'morality items mapped')

    #for item in relic:
    #  print(item['Type'],item['enchants'])
    for item in morality:
      print(item['Type'],item['enchants'])

