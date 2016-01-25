#!/bin/sh

. ./common.sh

license() {
	echo "${LICENSE}"
}

LICENSES="$(common_iterate license common_void)"

echo $(echo "${LICENSES}" | sort | uniq | sed 's/$/ and/') | sed 's/ and$//'
