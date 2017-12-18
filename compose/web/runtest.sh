#!/usr/bin/env sh
GREEN='\033[0;32m'
NC='\033[0m'

isort --check-only -q || exit 1
echo -e "${GREEN}isort: OK${NC}"

pylint discuss/* --errors-only || exit 1
echo -e "${GREEN}pylint: OK${NC}"

pytest discuss --cov-report term
