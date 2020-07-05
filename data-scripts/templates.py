#!/usr/bin/env python3

# A set of Javascript templates, for use with Python's str.format()

################################################################################

DATA_TEMPLATE='''
function Slot(name) {{
  this.name = name
}}

var slots = [
{slots}
];

// Object constructor
function Enchant(name, str, items, slots, quality, groups, range) {{
  this.name = name;
  this.str = str;
  this.items = items;
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

################################################################################

ENCHANT_TEMPLATE='''new Enchant('{name}',
              "{desc}",
              [{items}],
              [{slots}],
              '{quality}',
              [{groups}]),
'''
