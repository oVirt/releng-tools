#!/bin/bash -e

# This script requires:
# - perl-XML-XPath
# - subversion


[ -d trunk ] && rm -rf trunk
URL="svn://svn.forge.objectweb.org/svnroot/spagobi/V_5.x/Server/trunk"
SVNREV=$(svn info --xml ${URL}|xpath "string(//entry/@revision)" 2>/dev/null)

svn export -r ${SVNREV} ${URL}

VERSION=$(xpath trunk/spagobi-parent/pom.xml  "//project/version/text()" 2>/dev/null)
CHECKOUT="$(date -u +%Y%m%d)svn${SVNREV}"

[ -f spagobi5x-${CHECKOUT}.tar.xz ] && rm -f spagobi5x-${CHECKOUT}.tar.xz
[ -d spagobi5x-${CHECKOUT} ] && rm -rf spagobi5x-${CHECKOUT}

cp -rl trunk spagobi5x-${CHECKOUT}
find spagobi5x-${CHECKOUT} -name "*.jar" -delete
rm -rf spagobi5x-${CHECKOUT}/.svn
tar -cJvf spagobi5x-${CHECKOUT}.tar.xz spagobi5x-${CHECKOUT}
rm -rf spagobi5x-${CHECKOUT}

# Generate the spec from the template:
sed \
    -e "s/@VERSION@/${VERSION}/g" \
    -e "s/@SVNREV@/${SVNREV}/g" \
    -e "s/@CHECKOUT@/${CHECKOUT}/g" \
    < "spagobi.spec.in" \
    > "spagobi.spec"

# Build the source and binary packages:
rpmbuild \
    -bs \
    --define="_sourcedir ${PWD}" \
    --define="_srcrpmdir ${PWD}" \
    --define="_rpmdir ${PWD}" \
    --define="_rpmfilename %{name}-%{version}-%{release}.%{arch}.rpm" \
    "spagobi.spec"
