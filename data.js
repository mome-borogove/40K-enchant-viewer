// Object constructor
function Enchant(name, str, slots, quality, groups, range) {
  this.name = name;
  this.str = str;
  this.slots = slots;
  this.quality = quality;
  this.groups = groups;
  this.range = range;
}

function Slot(name) {
  this.name = name
}

var slots = [
  Slot('neural_implant'),
  Slot('eye_implant'),
  Slot('main_implant'),
  Slot('purity_seal'),
  Slot('belt'),
  Slot('body_armour'),
  Slot('inoculator'),
  Slot('weapon1'),
  Slot('signum1'),
  Slot('signum2'),
  Slot('weapon2')
];

var enchant_data = new Map()

var enchants = [
  new Enchant('critical_hit_chance_major',
          'Increase critical hit chance.',
          ['weapon_1h','weapon_2h','signum','eye_implant'],
          'primary',
          [],
          [0.04,0.06]),
  new Enchant('critical_hit_strength_major',
          '{X} critical strength.',
          ['weapon_1h','weapon_2h','signum','eye_implant'],
          'primary',
          ['critical_hit_strength'],
          [0.04,0.06]),
  new Enchant('Critical_damage_bonus',
          '{X}% critical damage.',
          ['weapon_1h','weapon_2h','signum'],
          'primary',
          ['critical_hit_strength'],
          [0.04,0.06]),
  new Enchant('Crit_chance_and_strenght_on_slow_group_major',
          '[ff2bede6]+5%[/ff2bede6] Critical Hit Chance and [ff2bede6]+10[/ff2bede6] Critical Hit Strength against [ff2bede6]Slowed[/ff2bede6], [ff2bede6]Shocked[/ff2bede6], [ff2bede6]Stunned[/ff2bede6] or [ff2bede6]Frozen[/ff2bede6] targets.',
          ['main_implant','eye_implant','armors'],
          'secondary',
          [],
          [0.06,0.1])
];


var enchant_groups = new Map()

enchant_groups.set('critical_hit_strength',
  ['critical_hit_strength_major','Critical_damage_bonus']);


