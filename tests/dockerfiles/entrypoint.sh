#!/bin/bash
nohup redis-server &
ln -s tests/_minqlx.py
ln -s tests/minqlx_plugin_test
ln -s tests/minqlx-repo/python/minqlx
coverage run -m unittest tests
coverage xml -o /output/coverage.xml
