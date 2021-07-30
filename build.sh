#!/bin/bash

PYTHONPATH=lib40k/ python3 scripts/gen_data_js.py data/VERSION data/enchantments.cfg data/Lang_Artifacts.xml data/inventoryitems.cfg data.js
sass --no-source-map scss:css
