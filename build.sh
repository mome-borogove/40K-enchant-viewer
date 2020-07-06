#!/bin/bash

python3 data-scripts/gen_data_js.py data/VERSION data/enchantments.cfg data/Lang_Artifacts.xml data/inventoryitems.cfg data.js
sass scss:css
