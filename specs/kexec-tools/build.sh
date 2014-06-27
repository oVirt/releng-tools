#!/bin/bash -e

help(){
    cat <<EOF
    Usage: $0 DISTRO OPTIONS

    PARAMETERS:
        DISTRO
            Distribution to build for, for example el6.

       OPTIONS
            Extra options to pass to the build scripts for the specific
            distribution
EOF
    exit $1
}


[[ -z "$1" ]] && help 1
[[ "$1" == "--help" ]] || [[ "$1" == "-h" ]] && help 0


[[ -e "$1"/build.sh ]] \
|| {
    echo "ERROR::Unable to find specific '$1' build.sh script at $build"
    help 1
}

pushd "$1"
shift 1
./build.sh "$@"
mv *src.rpm ../
