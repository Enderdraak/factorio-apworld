#!/bin/sh

set -e

cd $(dirname $(dirname $0))

CONFIG="$1"

WORLD="factorio_$CONFIG"

# Create build folders
mkdir --parents build output

# Remove old builds
rm --force --recursive "build/$WORLD"
rm --force "output/$WORLD.apworld"

# Build
cp --recursive base "build/$WORLD"

rm "build/$WORLD/debug.py"

rsync --recursive --ignore-times "config/$CONFIG/" "build/$WORLD/"

cp LICENSE "build/$WORLD"

# Dump data
PYTHONPATH="build/$WORLD/" python3 scripts/dump_data.py > "build/$WORLD/data/generated.py"

rm "build/$WORLD/data.json" "build/$WORLD/data/raw.py" "build/$WORLD/data/raw_base.py"
mv "build/$WORLD/data/generated.py" "build/$WORLD/data/raw.py"

# Create archipelago.json
GAME_NAME=$(PYTHONPATH="build/$WORLD" python3 -c "from config import game_name ; print(game_name)")

cat << EOF > "build/$WORLD/archipelago.json"
{
    "game": "$GAME_NAME",
    "world_version": "0.0.0",
    "compatible_version": 7
}
EOF

# Create .apworld
(cd build && zip --recurse-paths "../output/$WORLD.apworld" "$WORLD" --exclude \*__pycache__\*)
