#!/bin/bash

set -euo pipefail

trap cleanup ERR

target="lambda.zip"
src="src/main.py"
deps=$(mktemp -d)

function cleanup {
    rm -r "$deps" || true
}

pip install -r requirements.txt --target "$deps"

cd "$deps"
zip -r9v "$OLDPWD"/$target .
cd -

zip -gjv $target $src

cleanup
