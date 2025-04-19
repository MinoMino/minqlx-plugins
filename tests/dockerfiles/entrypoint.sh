#!/bin/bash
nohup redis-server &
ln -s tests/_minqlx.py
ln -s tests/minqlx_plugin_test
ln -s tests/minqlx-repo/python/minqlx
python3 -m unittest tests
