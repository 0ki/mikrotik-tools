#!/bin/bash
# (C) Kirils Solovjovs, 2017

[ -z "$1" ] && echo "Usage: $0 <filename.npk>" && exit 1
[ ! -f "$1" ] && echo "File not found." && exit 2
folder="$(echo $1 | rev | cut -d \.  -f 2- | cut -d \- -f 1 | rev )"
mkdir -p "./$folder"
unnpk -xf $1 -C "./$folder"
cd "./$folder"
[ -f "system.squashfs" ] && unsquashfs system.squashfs
