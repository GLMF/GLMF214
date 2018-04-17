#!/bin/bash
#SlackDeps, copyright Frank ENDRES, 2018-01-05
#This software is governed by the CeCILL license under French law.


function check_system () { #lookup missing shared object files in whole system
	touch /tmp/missinglibs.$$
	touch /tmp/faileddeps.$$
	find /bin /sbin /usr/bin /usr/sbin /usr/libexec -type f | xargs file | grep ELF | cut -f1 -d: | while read file; do
		ldd $file | grep "not found" | awk '{print $1}' | while read lib; do #search missing libs
			echo $file:$lib >> /tmp/faileddeps.$$
			if ! grep -q "^$lib$" /tmp/missinglibs.$$ ; then
				echo $lib >> /tmp/missinglibs.$$
			fi
		done
	done
}


function check_package () {
	cat $pkgfile | grep -v : | while read file; do #for each file in package
		if file /$file | grep -q ELF; then #if it is an ELF file
			ldd /$file | grep "not found" | awk '{print $1}' | while read lib; do
				echo $pkg:/$file:$lib >> /tmp/faileddeps.$$
				if ! grep -q "^$lib$" /tmp/missinglibs.$$; then
					echo $lib >> /tmp/missinglibs.$$
				fi
			done
		fi
	done
}


function check_install () { #lookup missing shared object files in packages (args)
	touch /tmp/missinglibs.$$
	touch /tmp/faileddeps.$$
	for pkg in $*; do
		pkgfile=$(grep -R "^$pkg:" /var/log/packages/ | cut -f1 -d: | sort -u)
		check_package
	done
}


function find_packages () { #search for packages containing missing libs
	touch /tmp/missingpkgs.$$
	cat /tmp/missinglibs.$$ | while read lib; do
		echo $lib:$(slackpkg file-search $lib | grep uninstalled | awk '{print $3}') >> /tmp/missingpkgs.$$
	done
}


function action_report () {
	opt=$1
	echo -e "\nFailed dependencies :"
	cat /tmp/faileddeps.$$
	echo -e "\nMissing libs :"
	cat /tmp/missinglibs.$$
	echo -e "\nPackages containing the missing libs :"
	cat /tmp/missingpkgs.$$
	rm -f /tmp/*.$$
}


function usage () {
	echo "usage: $0 missing"
	echo "usage: $0 install paquage1 paquage2 ..."
	exit
}


case "$1" in
	"missing")
		check_system
		find_packages
		action_report
	;;
	"install")
		shift
		if (( $# == 0 )); then usage; fi
		slackpkg install $*
		check_install $*
		find_packages
		action_report
	;;
	*) usage
esac
