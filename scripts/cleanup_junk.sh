#!/bin/bash
find . -name '*~' -exec rm {} \;
find . -name '*.pyc' -exec rm {} \;
find . -name '*.new' -exec rm {} \;
rm -rf servers/tornado/templates
rm -rf servers/tornado/output
