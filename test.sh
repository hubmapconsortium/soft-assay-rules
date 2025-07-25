#!/usr/bin/env bash
set -o errexit
die() { set +v; echo "$*" 1>&2 ; exit 1; }

red="$(tput setaf 1)"
green="$(tput setaf 2)"
reset="$(tput sgr0)"

start() { [[ -z "$CI" ]] || echo "travis_fold:start:$1"; echo "$green$1$reset"; }
end() { [[ -z "$CI" ]] || echo "travis_fold:end:$1"; }
die() { set +v; echo "$red$*$reset" 1>&2 ; exit 1; }


start placeholder
python tests/pytest_runner.py
end placeholder
