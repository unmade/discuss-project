#!/usr/bin/env sh
isort --check-only -q || exit 1
pylint discuss/* --errors-only || exit 1
pytest discuss --cov-report term
