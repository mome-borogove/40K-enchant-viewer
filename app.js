////////////////////////////////////////////////////////////////////////////////
// Utilities

// Vue 2 has trouble with true maps. It cannot react to changes in them.
// Since we'd like to use a 2-level map to track the different filters we have,
// this causes us a bit of a headache.
//
// Vue 2 *can*, however, react to changes in arrays, and since the list of keys
// is essentially static, we elect to solve things by using an additional
// layer of indirection.
//
// We arbitrarily map each key pair to contiguous integers. These can be used
// as indices into a boolean array which can be held and tracked by Vue.
//
// In other words, Vue just sees an array of boolean values that are getting
// flipped, and we use an un-tracked auxiliary map to assign human names
// to the indices.
//
// In pratice, the idiom will look something like this:
//     F_mask[ FMap.get2('filter-type', 'filter-value') ]
// Where F_mask is the boolean array, FMap is this static 2-level auxiliary map,
// 'filter-type' is the high-level filter category (like 'slot' or 'season'),
// and 'filter-value' is the value you're filtering on (like 'main_weapon').
// Sure, it's a little more cumbersome than if Vue 2 had native map support
// (where the expression would look like "F_mask['filter-type']['filter-value']")
// but it's good enough.
//
// Wheeler and Lampson would be proud.
var FMap;
{
  let _FMap_counter = 0;
  function _enum(s) { return [s, _FMap_counter++]; }
  // These are our static keys. Should we need more in the future, add them here.
  FMap = new Map([
    ['quality',
     new Map([
               'primary','secondary','relic','archeo','puritan','radical',
             ].map(_enum))],
    ['slot', new Map(SLOTS.map(_enum))],
    ['season', new Map([0,1,2,3,4,5].map(_enum))],
    ['item', new Map(SLOTS.map(s=>slot_items.get(s)).flat().sort().map(_enum))],
  ]);
  // Shortcut function for 2-level accessor (FMap.get(x).get(y))
  function _get2(k0, k1) {
    return this.get(k0).get(k1);
  }
  FMap.get2 = _get2;
  // I use arrays of keys and values a lot, so an Array.from shortcut is helpful.
  function _getarray(self, key, func) {
    var a;
    if( key==undefined ) { // If no key, then flatten the whole FMap
      return Array.from(self.values()).map(v => Array.from(func(v))).flat();
    } else {
      return Array.from(func(self.get(key)));
    }
  }
  function _key_array(key) {
    return _getarray(this, key, submap => submap.keys());
  }
  FMap.key_array = _key_array;
  function _value_array(key) {
    return _getarray(this, key, submap => submap.values());
  }
  FMap.value_array = _value_array;
}
 
////////////////////////////////////////////////////////////////////////////////
// Components

// Reusable filter button
Vue.component('toggle-button', {
  model: {
    prop: 'value',
    event: 'MouseEvent'
  },
  props: {
    value: Boolean,
    color: String,
  },
  template: `
    <button type="button"
            class="btn"
            :class="['btn-outline-'+color,
                     {'active': value}]"
            @click="_click">
      <slot></slot>
    </button>`,
  methods: {
    _click: function () {
      this.value = !this.value;
      this.$emit('MouseEvent', this.value);
    }
  },
});

// Filter "button" for slot imagemap
Vue.component('toggle-area', {
  model: {
    prop: 'value',
    event: 'MouseEvent'
  },
  props: {
    value: Boolean,
    slot: String,
    rect: Boolean,
  },
  template: `
    <a :id="'A_'+slot"
       class="area area_square"
       :class="{ 'active': value,
                 'area_rect': rect,
                 'area_square': !rect
               }"
       @click="_click"></a>`,
  methods: {
    _click: function () {
      this.value = !this.value;
      this.$emit('MouseEvent', this.value);
    }
  },
});


////////////////////////////////////////////////////////////////////////////////
// Static Data
var STATIC;
{
  var _colors = ['primary','secondary','relic','archeo','puritan','radical'];
  DATA = {
    color_map: new Map(FMap.key_array('quality').map((q,idx)=>[q,_colors[idx]])),
  }
}


////////////////////////////////////////////////////////////////////////////////
// App

// Define a filter object. This provides the enchant table everything it
// needs to down-select the desired enchants.
function Filter(pattern, slots, qualities) {
  this.pattern = pattern;
  this.slots = slots;
  this.qualities = qualities;
}

var empty_filter = new Filter("", new Set([]), new Set(['primary']));

function toggle_control_status(control, tag='active') {
  control.classList.toggle(tag);
}
function get_control_status(control, tag='active') {
  return control.classList.contains(tag);
}

var app = new Vue({
  el: "#app",
  data: function() {
    return {
      enchants: enchants,
      F_mask: undefined,
      F_pattern: "",

      enchant_fields: [
        { key:'str', label:'Enchant Name', sortable:false },
        { key:'show_details', label:'', sortable:false },
      ],

    }
  },
  created: function() {
    // Set initial masks
    this.F_mask = FMap.key_array().map(_ => false);
    this.$set(this.F_mask, FMap.get2('quality','primary'), true);
    this.$set(this.F_mask, FMap.get2('season',0), true);
    // Sorry, console users...
    //this.$set(this.F_mask, FMap.get2('season',5), true);
  },
  watch: {
    // Enforce data dependence constraints
    // WARNING: Be careful with this. This function *must* have a fixpoint.
    // Infinite compute loops are not good.
    F_mask:
      function (new_mask, old_mask) {
        // (1) Item type filters should always be cleared
        for ([slot,s_idx] of FMap.get('slot')) {
          if( ! new_mask[s_idx] ) {
            for (item of slot_items.get(slot)) {
              i_idx = FMap.get2('item',item);
              new_mask[i_idx] = false;
            }
          }
        }
        // Now update the entire array.
        //
        // In order for constraint updates to converge, this must only be done
        // *once* here at the end, otherwise elementwise changes to F_mask will
        // re-trigger the whole watch function (and all of its changes). That
        // will cause an infinite loop.
        this.$set(this.F_mask, new_mask);
      }
  },
  computed: {
    all_slots: function() {
      return FMap.key_array('slot');
    },
    rect_slots: function() {
      return RECT_SLOTS;
    },
    version: function() {
      return __version__; // defined in data.js
    },
    any_slot_selected() {
      return FMap.value_array('slot').some(i=>this.F_mask[i]);
    },
    any_item_selected() {
      return FMap.value_array('item').some(i=>this.F_mask[i]);
    },
    available_items: function() {
      return SLOTS.filter(s=>this.F_mask[FMap.get2('slot',s)])
                  .map(s => slot_items.get(s))
                  .flat()
                  .sort();
    },
    filtered_enchants: function() {
      return this.enchants.filter(e => this.filter_function(e, this.F_pattern, this.F_mask));
    },
    // Static Data
    color_map: function() {
      return DATA.color_map;
    }
  },
  methods: {
    filter_function(enchant, pattern, mask) {
      // Quality
      if( !mask[FMap.get2('quality', enchant.quality)] ) {
        return false;
      }
      // Filter by slot
      if( this.any_slot_selected ) {
        if( this.any_item_selected ) { // slot(s) AND item(s) selected
          if( !enchant.items.some(i => mask[FMap.get2('item', i)]) ) {
            return false;
          }
        } else { // Just slot(s), no item(s)
          if( !enchant.slots.some(s => mask[FMap.get2('slot', s)]) ) {
            return false;
          }
        }
      }
      // Filter by season
      if( !enchant.seasons.some(s => mask[FMap.get2('season',s)]) ) {
        return false;
      }
      // Filter by text
      if (pattern &&
         !enchant.str.toLowerCase().includes(pattern.toLowerCase())) {
        return false;
      }

      return true; // Display if not filtered out
    },
    is_seasonal(enchant) {
      if( (enchant.seasons!=undefined) &&
          (enchant.seasons.length>0) &&
          (!enchant.seasons.includes(0)) ) {
        return true;
      }
      return false;
    },
    clear_filter() {
      this.current_filter = empty_filter;
    },
    select_pattern(pattern) {
      this.F_pattern = pattern.toLowerCase();
    },
    clear_pattern(pattern) {
      this.F_pattern = "";
    },
    clear_slots() {
      for ([slot,idx] of FMap.get('slot')) {
        this.$set(this.F_mask, idx, false);
      }
    },
    items_for_selected_slot(slot) {
      return slot_items.get(slot);
    },
    capitalize(s) {
      return s.charAt(0).toUpperCase() + s.slice(1);
    }
  }
});


//app.mount('#app')
