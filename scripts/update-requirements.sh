#!/bin/bash
# Update all requirements files
pip-compile requirements/base.in -o requirements/base.txt
pip-compile requirements/dev.in -o requirements/dev.txt
pip-compile requirements/test.in -o requirements/test.txt
pip-compile requirements/prod.in -o requirements/prod.txt
