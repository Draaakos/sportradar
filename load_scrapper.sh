#!/bin/bash

# scrappers=(fotmob, goal, sportradar, betapi)
scrappers=(fotmob, goal, sportradar)

execute_scrapper() {
    echo "loading virtualenvironment for python"

    source ./envs/bin/activate
    directory_name=$(dirname $BASH_SOURCE)
    cd $directory_name
    python3.11 -m scripts.$1
}

for i in "${scrappers[@]}"
do
    if [ "$i" == $1 ] ; then
        execute_scrapper $1
        exit 0
    fi
done

echo "there is no $1 on your processor list"
exit -1
