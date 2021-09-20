#!/bin/bash

date

export MASTER="/var/www/html/pub/ovirt-master-snapshot/rpm/el8/noarch"
export OVIRT44="/var/www/html/pub/ovirt-4.4-snapshot/rpm/el8/noarch"
export YUMREPO="/var/www/html/pub/yum-repo"

ln -sf "$(ls "${MASTER}"/ovirt-release-master-4* |tail -n 1)" "${YUMREPO}/ovirt-release-master.rpm"
ln -sf "$(ls "${OVIRT44}"/ovirt-release44-snapshot-4* |tail -n 1)" "${YUMREPO}/ovirt-release44-snapshot.rpm"
echo "-------------------------------"
