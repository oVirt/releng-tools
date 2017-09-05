#!/bin/bash

export MASTER="/var/www/html/pub/ovirt-master-snapshot/rpm/el7/noarch"
export OVIRT41="/var/www/html/pub/ovirt-4.1-snapshot/rpm/el7/noarch"
export YUMREPO="/var/www/html/pub/yum-repo"

ln -sf `ls "${MASTER}"/ovirt-release-master-4* |tail -n 1` "${YUMREPO}/ovirt-release-master.rpm"
ln -sf `ls "${MASTER}"/ovirt-release-master-experimental-4* |tail -n 1` "${YUMREPO}/ovirt-release-master-experimental.rpm"
ln -sf `ls "${OVIRT41}"/ovirt-release41-snapshot-4* |tail -n 1` "${YUMREPO}/ovirt-release41-snapshot.rpm"
