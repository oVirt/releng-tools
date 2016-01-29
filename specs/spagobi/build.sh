#!/bin/bash -e

# This script requires:
# - perl-XML-XPath
# - subversion


[ -d trunk ] && rm -rf trunk
URL="svn://svn.forge.objectweb.org/svnroot/spagobi/V_5.x/Server/branches/SpagoBI-5.2"
SVNREV=$(svn info --xml ${URL}|xpath "string(//entry/@revision)" 2>/dev/null)

DIRS=(
#     cas
#     SpagoBIBirtReportEngine
    spagobi-core
#     SpagoBIJPivotEngine
    SpagoBIOAuth2SecurityProvider
#     SpagoBITalendEngineCilentAPI
#     ChefCookbooks
#     SpagoBIChartEngine
    SpagoBIDAO
    SpagoBILdapSecurityProvider
    SpagoBIUtils
    QbeCore
#     SpagoBICockpitEngine
    SpagoBIDatabaseScripts
    SpagoBILiferaySecurityProvider
    SpagoBIProject
    SpagoBIUtilsJSON
#     resources
#     SpagoBICommonJEngine
#     SpagoBIDataMiningEngine
    spagobi-metamodel-core
    SpagoBIQbeEngine
#     SpagoBIWhatIfEngine
#     Servers
    spagobi-commons-core
#     SpagoBIGeoEngine
    spagobi-metamodel-utils
#     SpagoBISDK
#     SpagoBIXXXSpagoEngine
#     SpagoBIAccessibilityEngine
#     SpagoBIComponent
#     SpagoBIGeoReportEngine
#     SpagoBIMobileEngine
#     SpagoBISocialAnalysis
#     spagobi.birt.oda
#     SpagoBIConsoleEngine
    SpagoBIJasperReportEngine
#     SpagoBINetworkEngine
#     SpagoBITalendEngine
)

mkdir trunk
svn export -r ${SVNREV} ${URL}/spagobi-parent trunk/spagobi-parent

VERSION=$(xpath trunk/spagobi-parent/pom.xml  "//project/version/text()" 2>/dev/null)
CHECKOUT="$(date -u +%Y%m%d)svn${SVNREV}"

echo "Building version ${VERSION}"

for project in "${DIRS[@]}"
do
    echo "Exporting ${project}"
    svn --quiet export -r ${SVNREV} ${URL}/${project} trunk/${project}
done



[ -f spagobi5x-${CHECKOUT}.tar.xz ] && rm -f spagobi5x-${CHECKOUT}.tar.xz
[ -d spagobi5x-${CHECKOUT} ] && rm -rf spagobi5x-${CHECKOUT}

cp -rl trunk spagobi5x-${CHECKOUT}
find spagobi5x-${CHECKOUT} -name "*.jar" -delete
rm -rf spagobi5x-${CHECKOUT}/.svn
tar --checkpoint=1000 -cJf spagobi5x-${CHECKOUT}.tar.xz spagobi5x-${CHECKOUT}
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
