#!/bin/bash

# ------------ ~ Get Argument(s) ~ ------------

res=600
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -n|--name) file_name="$2"; shift 2;;
	-r|--resolution) res="$2"; shift 2;;
	*) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [[ ! "$file_name" ]]; then
    echo "No file name specified"
    exit 3
fi

# ------------ ~ Actual script starts here ~ ------------

echo "Starting scan utility with output file: \"$file_name\" with resolution $res"

scanimage > "$file_name".jpg --format jpeg --resolution="$res" -p

