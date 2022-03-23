#!/usr/bin/python3

from release_notes_git import Bugzilla
import os
import sys


def main(milestone):
    if not os.path.exists('milestones/%s.conf' % milestone):
        sys.exit('Invalid milestone: %s' % (milestone))
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
        elif(bug.product == 'ovirt-engine'):
            if (bug.component == 'ovirt-engine-ui-extensions'):
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
            print(
                " |- https://bugzilla.redhat.com/"
                "show_bug.cgi?id={v}".format(v=v)
            )


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Please specify a milestone like: ovirt-4.5.0')
    milestone = sys.argv[1]
    main(milestone)
