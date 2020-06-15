// Define a filter object. This provides the enchant table everything it
// needs to down-select the desired enchants.
function Filter(str, slot, quality) {
  this.str = str;
  this.slot = slot;
  this.quality = quality;
}
var empty_filter = new Filter(null, null, new Set(['primary']));

var app = new Vue({
  el: "#app",
  data: {
    enchants: enchants,
    current_filter: empty_filter,
    enchant_fields: [ 'name', 'str' ],
  },
  methods: {
    filter_function(enchant, filter) {
      // Filter by quality
      if (!filter.quality.has(enchant.quality)) {
        return false;
      }
      // Filter by slot
      if ((filter.slot!==null) && (!enchant.slots.includes(filter.slot))) {
        return false;
      }

      return true; // Display if not filtered out
    },
    clear_filter() {
      this.current_filter = empty_filter;
    },
    select_quality(event, quality) {
      // Update control
      let button = event.target;
      button.classList.toggle('active');
      // Update filter
      if (button.classList.contains('active')) {
        this.current_filter.quality.add(quality);
      } else {
        this.current_filter.quality.delete(quality);
      }
      // Vue doesn't detect object mutation. Manually trigger refresh.
      this.$root.$emit('bv::refresh::table', 'enchants')
    },
    select_slot(event, slot) {
      console.log(event);
      console.log(slot);
    },
    select_enchant(enchant, idx, event) {
      console.log(enchant);
    }
  }
});

