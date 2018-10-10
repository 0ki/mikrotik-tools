#!/bin/bash
# (C) Kirils Solovjovs, 2018

if [ "$(ps -o comm= $PPID)" == "ssh" ]; then
	cat /tmp/.pass
	exit 0
fi


function cleanup {
  rm /tmp/.pass 2> /dev/null
  rm -- /tmp/jb_c_* 2> /dev/null
}

trap cleanup EXIT


vercomp () {
    #(C) Dennis Williamson, 2010, https://stackoverflow.com/questions/4023830/how-to-compare-two-strings-in-dot-separated-version-format-in-bash
    if [[ $1 == $2 ]]
    then
        return 0
    fi
    local IFS=.
    local i ver1=($1) ver2=($2)
    # fill empty fields in ver1 with zeros
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++))
    do
        ver1[i]=0
    done
    for ((i=0; i<${#ver1[@]}; i++))
    do
        if [[ -z ${ver2[i]} ]]
        then
            # fill empty fields in ver2 with zeros
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]}))
        then
            return 1
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]}))
        then
            return 2
        fi
    done
    return 0
}


cd "$(dirname "$(echo $0)")"

rm /tmp/PASSOUT 2> /dev/null
echo "* Not affiliated with Mikrotikls or Oracle *"
echo
echo "Welcome to jailbreak tool v2.00 for MikroTik devices"
echo "                                    by PossibleSecurity.com"
echo 
echo "WARNING! THIS TOOL MAY BRICK YOUR DEVICE. USE AT YOUR OWN RISK."
echo "AUTHORS OF THIS TOOL MAY NOT BE HOLD LIABLE FOR ANY DIRECT OR"
echo "INDIRECT DAMAGES CAUSED AS A RESULT OF USING THIS TOOL."
echo 
echo "Plug in the magic USB into the router now!"
echo "If <<brick>> happens, go for netinstall to recover."
echo 
echo " * * * * * * * * "

JBID="jb_c_$$_$RANDOM"

echo "We'll need the IP address of the device, user and password."
while true; do
	echo -n "IP [192.168.88.1]: "
	read IP
	echo "USER [admin]: admin"
	USER="admin"
	echo -n "PASS []: "
	read PASS
	[ "$IP" == "" ] && IP="192.168.88.1"
	echo 
	echo "We got $USER@$IP with password '$PASS'."
	while true; do
		echo -n "Is this correct? (y/N) "
		read confirm
		[ -z "$confirm" ] && echo "Please enter 'yes' or 'no'!" || break
	done

	[ "${confirm:0:1}" == "y" -o "${confirm:0:1}" == "Y" ] && break
	echo "Try again, please."
done


echo -n "$PASS" > /tmp/.pass

echo 
echo "Let's begin."

ping -c1 $IP &> /dev/null
[ $? -ne 0 ] && echo ERROR: IP address must respond to ICMP echo requests. && exit 1



echo "Verifying version..."
res="$(DISPLAY="none" SSH_ASKPASS="$0" setsid ssh -oHostKeyAlgorithms=+ssh-dss -oKexAlgorithms=diffie-hellman-group1-sha1,diffie-hellman-group14-sha1 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -l "$USER" "$IP" "/system resource print" 2>/dev/null )"
[ "$?" -ne "0" ] && echo ERROR: Unable to connect to $IP:22 with user $USER. && exit 1

arch="$(echo $res |tr $'\r' $'\n'| grep architecture-name |cut -d : -f 2|tr -dc [a-zA-Z0-9]_ )"
version="$(echo $res |tr $'\r' $'\n'| grep version |cut -d : -f 2|cut -d \( -f 1|tr -dc [a-zA-Z0-9]._ )"

version_cmp="$(echo $version | sed s/rc.*$//)"
version_rc="$(echo $version |grep rc | sed s/^.*rc//)"

vercomp "$version_cmp" "6.41"
[ $? -eq 2 ] && echo "Software $version is not supported by this tool. The first supported version is 6.41rc1. Use exploit_backup for older versions." && exit 9


echo "; mkdir /pckg/option; mount -o bind /boot/ /pckg/option; ln -s / /rw/pckg/.root;" > /tmp/$JBID

echo -n "Trying to enable jailbreak..."

success="0"
for ((i=0;i<=5;i++)); do
	echo -n "$i..."
	[ $i -eq 0 ] && disk="/" || disk="/disk$i/"
	DISPLAY="none" SSH_ASKPASS="$0" setsid scp -oHostKeyAlgorithms=+ssh-dss -oKexAlgorithms=diffie-hellman-group1-sha1,diffie-hellman-group14-sha1 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "/tmp/$JBID" "$USER@$IP:$disk.root/rw/DEFCONF"  2> /dev/null
	[ "$?" -eq "0" ] && success="1" && echo "success" && break
done

[ "$success" -eq "0" ] && echo ERROR: Unable to upload jailbreak to $IP:22 with user $USER. Are you sure that 'magic' USB is connected? && exit 1

res="$(DISPLAY="none" SSH_ASKPASS="$0" setsid ssh -oHostKeyAlgorithms=+ssh-dss -oKexAlgorithms=diffie-hellman-group1-sha1,diffie-hellman-group14-sha1 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -l "$USER" "$IP" "/system reboot" 2> /dev/null)"

st=$?

[ "$st" -ne "0" -a "$st" -ne "255" ] && echo ERROR: Unable to order reboot. Please reboot manually and ssh with user devel. && exit 1
# st == 255 on too fast disconnect too

echo "Waiting for device to reboot..."
sleep 10

echo "Waiting for device to become available..."
until ping -c1 $IP &>/dev/null; do :; done

echo "Loading your one time shell... Enjoy!"
SSH_ASKPASS="$0" setsid ssh -oHostKeyAlgorithms=+ssh-dss -oKexAlgorithms=diffie-hellman-group1-sha1,diffie-hellman-group14-sha1 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -l "devel" "$IP"


