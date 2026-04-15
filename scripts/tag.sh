#!/bin/sh

set -e

FILE=$(realpath "$1")
VERSION="$2"

DIR=$(basename --suffix=.apworld "$FILE")

TMP=$(mktemp --directory)

cd "$TMP"

unzip "$FILE" "$DIR/archipelago.json"
sed --in-place --expression "s/\"world_version\": \"0.0.0\"/\"world_version\": \"$VERSION\"/" "$DIR/archipelago.json"
zip "$FILE" "$DIR/archipelago.json"

cd

rm "$TMP/$DIR/archipelago.json"
rmdir "$TMP/$DIR"
rmdir "$TMP"
