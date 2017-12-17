#!/usr/bin/env sh
isort --check-only -q
pylint discuss/* --errors-only
pytest discuss
