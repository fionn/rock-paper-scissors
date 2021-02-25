#!/bin/bash

set -Eeo pipefail

trap cleanup ERR

function cleanup {
    rm -r "$deps" || true
    echo "Cleaning up $deps"
}

set -u

function main {
    readonly target="$1"
    local -r src="$2"

    readonly deps=$(mktemp -d)

    pip install -r requirements.txt --target "$deps"

    pushd "$deps"
    zip -r9vZb "$OLDPWD"/"$target" .
    popd

    zip -gjv "$target" "$src"

    readonly checksum=$(sha256sum "$target" | cut -d " " -f 1)
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@" >&2
    jq -n '$ARGS.named' --arg filename "$target" --arg checksum "$checksum" --arg path "$(pwd)/$target"
    cleanup >&2
fi
