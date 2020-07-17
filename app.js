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
  data: {
    enchants: enchants,
    F_pattern: "",
    F_slots: [],
    F_qualities: ['primary'],
    F_items: [],
    enchant_fields: [
      { key:'str', label:'Enchant Name', sortable:false },
      { key:'show_details', label:'', sortable:false },
    ],
  },
  computed: {
    all_slots: function() {
      return SLOTS;
    },
    rect_slots: function() {
      return RECT_SLOTS;
    },
    version: function() {
      return __version__; // defined in data.js
    },
    current_items: function() {
      return this.F_slots
                 .map(s => slot_items.get(s))
                 .flat()
                 .filter((s,i,a) => a.indexOf(s)==i)
                 .sort();
    }
  },
  methods: {
    filter_function(enchant, args) {
      let pattern=args[0];
      let slots=args[1];
      let qualities=args[2];
      let items=args[3];
      // Filter by quality
      if (!qualities.includes(enchant.quality)) {
        return false;
      }
      // Filter by slot
      if (slots.length>0) {
        // Filter by item if any are selected
        if (items.length>0) {
          if (!enchant.items.some(x => items.includes(x))) {
            return false;
          }
        } else {
          if (!enchant.slots.some(x => slots.includes(x))) {
            return false;
          }
        }
      }
      // Filter by text
      if (pattern &&
         !enchant.str.toLowerCase().includes(pattern.toLowerCase())) {
        return false;
      }

      return true; // Display if not filtered out
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
    toggle_quality(quality) {
      // Update filter
      if (this.F_qualities.includes(quality)) {
        this.F_qualities.splice(this.F_qualities.indexOf(quality), 1);
      } else {
        this.F_qualities.push(quality);
      }
    },
    toggle_slot(slot) {
      if (this.F_slots.includes(slot)) {
        this.F_slots.splice(this.F_slots.indexOf(slot), 1);
        // Also remove all selected items from this slot.
        let items = this.items_for_selected_slot(slot);
        for(let i=0; i<items.length; i++) {
          let index = this.F_items.indexOf(items[i]);
          if (index>=0) {
            this.F_items.splice(index,1);
          }
        }
      } else {
        this.F_slots.push(slot);
      }
    },
    toggle_item(item) {
      if (this.F_items.includes(item)) {
        this.F_items.splice(this.F_items.indexOf(item), 1);
      } else {
        this.F_items.push(item);
      }
    },
    items_for_selected_slot(slot) {
      return slot_items.get(slot);
    },
  }
});

