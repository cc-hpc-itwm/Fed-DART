#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
bundle_paths=("$DIR/libexec/bundle/lib/*" "$DIR/libexec/bundle/gpispace/libexec/bundle/lib/*")
skips=()
forces=()

# Checks if an element is in a list, usage contains aList anElement
contains() {
    [[ $1 =~ (^|[[:space:]])"$2"($|[[:space:]]) ]] && return 0 || return 1
}

# Performs the unbundle operation
unbundle()
{
  files_to_rename=()

  for file in ${bundle_paths[@]}
  do
    echo -n "Checking $(basename $file)"
    alternative=$(ldconfig -p | grep $(basename $file) | awk '{print $NF}')
  
    contains ${skips[@]} $(basename $file)
	if [[ $? == 0 ]]
	then
	  echo " (skipped)"
	  continue
	fi
	
    if [[ -z "$alternative" ]]
    then
	  echo " (no alternative)"
	else
	#echo "File is $file"
    #echo "Found alternative for $(basename -- $alternative)"
    
	  # We found an alternative, check if we have to force using the alternative
      contains ${forces[@]} $(basename $file)
      if [[ $? == 0 ]]
      then
	    files_to_rename+=("$file")
	    echo " (forced)"
	    continue
      fi

      glibc_strings=$(strings $file | awk '/^GLIBC_/')
	  is_newer=1
	  for string in ${glibc_strings[@]}
	  do
	    found=$(strings $alternative | grep $string | awk '{print $NF}')
	    if [[ -z "$found" ]]
	    then
	      is_newer=0
	      break
	    fi
	  done
	
	  glibcxx_strings=$(strings $file | awk '/^GLIBCXX_/')
	  is_newer=1
	  for string in ${glibcxx_strings[@]}
	  do
	    found=$(strings $alternative | grep $string | awk '{print $NF}')
	    if [[ -z "$found" ]]
	    then
	      is_newer=0
		  break
	    fi
	  done
	  if [[ $is_newer -eq 1 ]]
	  then
        echo " (found alternative)"
	    files_to_rename+=("$file")
	  fi
    fi
    #echo "---------"
  done

  for file in ${files_to_rename[@]}
  do
    mv $file "$(dirname $file)/_$(basename $file)"
  done
}

rebundle()
{
  echo "Rebundling"
  for file in ${bundle_paths[@]}
  do
    if [[ ! -z "$(basename $file | awk '/^_/')" ]]
	then
	  base=$(basename $file)
	  mv $file "$(dirname $file)/${base:1}"
	fi
  done
}

while getopts "s:f:hr" opt; do
    case $opt in
        s) skips+=("$OPTARG");;
		f) forces+=("$OPTARG");;
		h) 
		  echo "Usage:"
		  echo " unbundle.sh [options]"
		  echo " unbundle.sh -r"
		  echo ""
		  echo "Tries to 'unbundle' the libraries, i.e., checks if there are newer libraries installed on the system. Newer means that the strings contains at least all of the GLIBC and GLIBCXX symbols of the bundled library."
		  echo ""
		  echo "Options:"
		  echo " -h             Displays this help"
		  echo " -s <name>      Skips the library with <name>"
		  echo " -f <name>      Forces the unbundling of <name>"
		  echo " -r             Rebundles the unbundled libraries"
		  exit 0
		;;
		r)
		  rebundle=1
    esac
done

if [[ -z "$rebundle" ]]
then
  unbundle
else
  rebundle
fi