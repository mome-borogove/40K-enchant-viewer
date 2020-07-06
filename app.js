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
function refresh_table(app) {
  // Vue doesn't detect object mutation. Manually trigger refresh.
  app.$root.$emit('bv::refresh::table', 'enchants');
}

var app = new Vue({
  el: "#app",
  data: {
    enchants: enchants,
    current_filter: empty_filter,
    selected_slots: [],
    pattern: null, // always all-lowercase
    enchant_fields: [
      { key:'str', label:'Enchant Name', sortable:false },
      { key:'show_details', label:'', sortable:false },
    ],
  },
  computed: {
    version: function() {
      return __version__; // defined in data.js
    }
  },
  methods: {
    filter_function(enchant, filter) {
      // Filter by quality
      if (!filter.qualities.has(enchant.quality)) {
        return false;
      }
      // Filter by slot
      if (filter.slots.size>0) {
        if (!enchant.slots.some(x => filter.slots.has(x))) {
          return false;
        }
      }
      // Filter by text
      if (filter.pattern &&
         !enchant.str.toLowerCase().includes(filter.pattern)) {
        return false;
      }

      return true; // Display if not filtered out
    },
    clear_filter() {
      this.current_filter = empty_filter;
    },
    select_pattern(pattern) {
      this.current_filter.pattern = pattern.toLowerCase();
      refresh_table(this);
    },
    clear_pattern(pattern) {
      this.pattern = null;
      this.select_pattern("");
    },
    select_quality(event, quality) {
      let button = event.target;
      // Update control
      toggle_control_status(button);
      // Update filter
      if (get_control_status(button)) {
        this.current_filter.qualities.add(quality);
      } else {
        this.current_filter.qualities.delete(quality);
      }
      refresh_table(this);
    },
    select_slot(event, slot) {
      let button = event.target;
      // Update control
      toggle_control_status(button);
      // Update filter
      if (get_control_status(button)) {
        this.current_filter.slots.add(slot);
        this.selected_slots.push(slot);
      } else {
        this.current_filter.slots.delete(slot);
        this.selected_slots.splice(this.selected_slots.indexOf(slot), 1);
      }
      refresh_table(this);
    },
    items_for_selected_slot(slot) {
      return slot_items.get(slot);
    },
  }
});

