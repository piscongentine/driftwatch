#!/usr/bin/env bash
# Records docs/demo.cast: the four demo commands typed into a real bash session (docs/demo.exp), 104 x 30 characters.
# Reads: docs/demo.exp and the whole project. Writes: docs/demo.cast (and, as the commands run, everything under out/).
# Needs a Linux shell with expect, asciinema, util-linux (for script) and the project requirements installed.
# Then turn the cast into a GIF: agg docs/demo.cast docs/assets/demo.gif --font-size 15 --theme github-dark --idle-time-limit 2.5 --last-frame-duration 7
set -eu
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
script -qec "stty cols 104 rows 30; asciinema rec --overwrite -q -c 'expect $root/docs/demo.exp' $root/docs/demo.cast" /dev/null
echo "cast written: $(wc -c < docs/demo.cast) bytes, $(wc -l < docs/demo.cast) lines"
