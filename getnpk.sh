#!/bin/bash

# (C) Kirils Solovjovs
# Beware! Script uses third party sources. You may get wrong stuff... or even worse.

[ -z "$1" ] && echo "Usage $0 <version>, e.g. $0 6.26" && exit 1
for x in $*; do
   ext="$(echo $x | rev | cut -d \. -f 1 |rev)"
	[ -z "$(echo $ext | grep -E "^[a-z]+$")" ] && ext="npk" || x="$(echo $x | rev | cut -d \. -f 2- |rev)"
	xp="${x//[^-]}"
	xp="${#xp}"
	[ "$xp" -eq "0" ] && name="routeros-x86-$x"
	[ "$xp" -eq "1" ] && name="routeros-$x"
	[ "$xp" -ge "2" ] && name="$x"

	name="$(echo $name | sed 's/^-//i')"

	x="$(echo $name| rev|cut -d \- -f 1|rev )"
	name="$name.$ext"

	[ -f "$name" ] && echo exists: $name && continue
	wget -q https://download2.mikrotik.com/routeros/$x/$name
	[ "$?" -eq "0" ] && echo done: $name && continue
	wget -q	http://upgrade.mikrotik.com/routeros/$x/$name
	[ "$?" -eq "0" ] && echo done: $name && continue
	wget -q http://admin.roset.cz/Mikrotik/routeros-ALL-$x/$name
	[ "$?" -eq "0" ] && echo done: $name && continue
	wget -q "http://mirror2.polsri.ac.id/MikroTik/RouterOS/RouterOS%20$x/$name"
	[ "$?" -eq "0" ] && echo done: $name && continue
	wget -q http://mirror.poliwangi.ac.id/mikrotik/$x/$name
	[ "$?" -eq "0" ] && echo done: $name && continue
	wget -q http://www.hlucin.net/mikrotik/$x/$name
	[ "$?" -eq "0" ] && echo done: $name && continue
	wget -q http://204.62.56.64/mikrotik/$x/$name
	[ "$?" -ne "0" ] && echo failed: $name || echo done: $name
done
