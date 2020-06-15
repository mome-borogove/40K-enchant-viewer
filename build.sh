#!/bin/bash

python3 data-scripts/gen_data_js.py data/enchantments.cfg data/Lang_Artifacts.xml data.js
sass scss:css
