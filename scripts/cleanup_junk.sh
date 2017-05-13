#!/bin/bash
find . -name '*~' -exec rm {} \;
find . -name '*.pyc' -exec rm {} \;
