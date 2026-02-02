#!/bin/bash
_yami() {   

	if [[ "$2" = -* ]] ; then 
		local cmd=$(yami -h | grep -Eo "^ *$2[^ ,-]+"  | grep -Eo '[^ ]*' )
		COMPREPLY=($(compgen -W "$cmd" ))
	else 
		if [ "$3" == "-j" ] ; then 
			local cmd=$(yami -jp names | grep -e "^$2" )
			COMPREPLY=($(compgen -W "$cmd")) ; 
		elif [ "$3" == "$1" ] || [ "$3" == "-e" ] ; then 
			local cmd=$(yami -p names | grep -e "^$2" )
			COMPREPLY=($(compgen -W "$cmd")) ; 
		else 
			true ;
			#local cmd=$(ls -a $(dirname $(realpath "$2"))) 
			#COMPREPLY=($(compgen -o filenames -W "$cmd"  -- "$2" )) ;
		fi 
	fi
}

complete -F _yami yami
