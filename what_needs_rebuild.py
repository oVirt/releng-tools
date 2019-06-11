#!/usr/bin/python3

from release_notes_git import Bugzilla
import sys


def main(milestone):
    bz = Bugzilla()
    bug_list = bz.get_bugs_in_milestone(milestone)
    products = {}
    for bug in bug_list:
        if bug.status != 'MODIFIED':
            # Assuming here that bugs are moved to QE only after a build is
            # available.
            continue
        if (bug.product == 'Red Hat Enterprise Virtualization Manager'):
            if (bug.component != 'Documentation'):
                products.setdefault(bug.component, [])
                products[bug.component].append(bug.id)
        else:
            products.setdefault(bug.product, [])
            products[bug.product].append(bug.id)
    print("The following products need to be built for {m}".format(
        m=milestone
    ))
    for p in products:
        print(" - {p}".format(p=p))
        for v in products[p]:
            print(" |- https://bugzilla.redhat.com/{v}".format(v=v))


if __name__ == '__main__':
    milestone = sys.argv[1]
    main(milestone)
