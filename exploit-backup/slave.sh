#!/bin/ash
# (C) Kirils Solovjovs, 2017

[ ! -f "busybox_p" ] && echo 888fail && exit 1

case "$PATH" in
	*/usr/local/bin*)
	# old versions
		dest="/usr/local/bin/"
	;;
	*)
		dest="/flash/bin/"
		if [ ! -d "/flash/" ]; then
			echo 888fail && exit 1
		fi
	;;
esac 

mkdir -p $dest

export PATH=$PATH:$dest

mv busybox_p $dest/busybox_p
chmod a+x $dest/busybox_p
cd $dest/
for target in "[" "[[" acpid add-shell addgroup adduser adjtimex arp arping ash awk base64 basename beep blkid blockdev bootchartd brctl bunzip2 bzcat bzip2 cal cat catv chat chattr chgrp chmod chown chpasswd chpst chroot chrt chvt cksum clear cmp comm conspy cp cpio crond crontab cryptpw cttyhack cut date dc dd deallocvt delgroup deluser depmod devmem df dhcprelay diff dirname dmesg dnsd dnsdomainname dos2unix du dumpkmap dumpleases echo ed egrep eject env envdir envuidgid ether-wake expand expr fakeidentd false fbset fbsplash fdflush fdformat fdisk fgconsole fgrep find findfs flock fold free freeramdisk fsck fsck.minix fsync ftpd ftpget ftpput fuser getopt getty grep groups gunzip gzip halt hd hdparm head hexdump hostid hostname httpd hush hwclock id ifconfig ifdown ifenslave ifplugd ifup inetd insmod install ionice iostat ip ipaddr ipcalc ipcrm ipcs iplink iproute iprule iptunnel kbd_mode kill killall killall5 klogd last less linux32 linux64 linuxrc ln loadfont loadkmap logger login logname logread losetup lpd lpq lpr ls lsattr lsmod lsof lspci lsusb lzcat lzma lzop lzopcat makedevs makemime man md5sum mdev mesg microcom mkdir mkdosfs mke2fs mkfifo mkfs.ext2 mkfs.minix mkfs.vfat mknod mkpasswd mkswap mktemp modinfo modprobe more mount mountpoint mpstat mt mv nameif nanddump nandwrite nbd-client nc netstat nice nmeter nohup nslookup ntpd od openvt passwd patch pgrep pidof ping ping6 pipe_progress pivot_root pkill pmap popmaildir powertop printenv printf ps pscan pstree pwd pwdx raidautorun rdate rdev readahead readlink readprofile realpath reformime remove-shell renice reset resize rev rm rmdir rmmod route rpm rpm2cpio rtcwake run-parts runlevel runsv runsvdir rx script scriptreplay sed sendmail seq setarch setconsole setfont setkeycodes setlogcons setserial setsid setuidgid sh sha1sum sha256sum sha3sum sha512sum showkey slattach sleep smemcap softlimit sort split start-stop-daemon stat strings stty su sulogin sum sv svlogd swapoff swapon switch_root sync sysctl syslogd tac tail tar tcpsvd tee telnet telnetd test tftp tftpd time timeout top touch tr traceroute traceroute6 true tty ttysize tunctl udhcpc udhcpd udpsvd umount uname unexpand uniq unix2dos unlzma unlzop unxz unzip uptime users usleep uudecode uuencode vconfig vi vlock volname wall watch watchdog wc wget which who whoami whois xargs xz xzcat yes zcat zcip; do
	ln -s busybox_p $target 2> /dev/null
done
sleep 1
sync
cd -

ln -s / .root

#do appreciate the dns magic :)
echo "nameserver 8.8.8.8" > /rw/resolve.conf
sed -i "s#/etc/resolv.conf#/rw/resolve.conf#" $dest/busybox_p

echo 888ok
sleep 1

rm slave.sh
