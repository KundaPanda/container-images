#!/bin/sh
set -eu

template_dist="/app/ombi-dist-template"
runtime_dist="/app/ombi/ClientApp/dist"

if [ ! -d "$runtime_dist" ]; then
    printf '%s\n' "error: missing frontend asset directory at $runtime_dist" >&2
    exit 1
fi

if [ ! -w "$runtime_dist" ]; then
    printf '%s\n' "error: $runtime_dist must be writable by the ombi user; mount a writable volume there when using a read-only root filesystem" >&2
    exit 1
fi

cp -R "$template_dist/." "$runtime_dist/"

exec /app/ombi/Ombi "$@"
