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
      # While "morality" is a quality, radical and puritan items are effectively
      # entirely separate item categories, and it's useful to treat them as such.
      # As a result, we split the 'morality' quality into two new, fake ones.
      #
      # Unfortunately, there isn't a given flag for this. Instead, we're forced
      # to parse the enchant name and extract it from there. I'm fairly sure
      # that Neocore is also scraping the name this way, so I'm assuming that
      # they won't give a non-morality enchant a name that starts with
      # 'blessed' or 'demonic'.
      if len([_ for _ in item['enchants'] if _.startswith('blessed')])>0:
        D['puritan'].append(item)
      elif len([_ for _ in item['enchants'] if _.startswith('demonic')])>0:
        D['radical'].append(item)
      else:
        print('Warning: morality item without tell-tale prefix:',item['name'])
        # And drop the enchant. What even is this?
  # default: drop the entry
  D['current_item'] = {}
  return _S.TOP 

def store_quality(M,D):
  D['current_item']['quality'] = M[0].split(',')

def store_enchants(M,D):
  D['current_item']['enchants'] = [str.lower(e) for e in M[0].split(',')]

# NOTE: The season data from inventoryitems.cfg is currently not used. This
# is left here merely for future convenience.
def store_seasons(M,D):
  # Although a single item doesn't ever exist across seasons (AFIAK), we still
  # store this as a list because it's possible that an enchant can. Later, we
  # unify this value with others, and having them all as lists simplifies that.
  D['current_item']['seasons'] = [ int(M[0]) ]

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
    (r'Season=(.*)', store_seasons),
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
  fsm.data = {'current_item': {}, 'relic': [], 'archeo': [], 'puritan': [], 'radical': []}
  #fsm.tracing(True)

  fsm.parse(file)
  return fsm.data['relic'], fsm.data['archeo'], fsm.data['puritan'], fsm.data['radical']


if __name__=='__main__':

  with open('inventoryitems.cfg') as f:
    relic, morality = parse_inventory(f)
    print(str(len(relic)),'relic items mapped')
    print(str(len(morality)),'morality items mapped')

    #for item in relic:
    #  print(item['Type'],item['enchants'])
    for item in morality:
      print(item['Type'],item['enchants'])

