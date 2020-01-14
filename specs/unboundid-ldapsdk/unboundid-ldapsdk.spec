# Build system requires too many stuff just to get the git hash of the
# tag used for building the tar.gz. Setting here.
%global commit c0fb784eebf9d36a67c736d0428fb3577f2e25bb

Name:           unboundid-ldapsdk
Version:        4.0.14
Release:        2%{?dist}
Summary:        UnboundID LDAP SDK for Java

License:        GPLv2 or LGPLv2+
URL:            https://www.ldap.com/unboundid-ldap-sdk-for-java
Source0:        https://github.com/pingidentity/ldapsdk/archive/%{version}.tar.gz
BuildArch:      noarch
BuildRequires:  ant
%if 0%{?fedora} || 0%{?rhel} >= 8
BuildRequires:  javapackages-local
%else
BuildRequires:  maven-local
%endif

%description
The UnboundID LDAP SDK for Java is a fast, powerful, user-friendly, and
completely free Java library for communicating with LDAP directory servers and
performing related tasks like reading and writing LDIF, encoding and
decoding data using base64 and ASN.1 BER, and performing secure communication.

%package javadoc
Summary:        Javadoc for %{name}

%description javadoc
This package contains the API documentation for %{name}.

%prep
%setup -q -n ldapsdk-%{version}
# remove external prebuilt libraries
rm -rf ext

%build
# checkstyle configuration files were in the ext directory
# code doesn't pass checkstyle 5.6 disabling the check until upstream
# fixes it
# upstream added code for getting exact git references for the build
# too many deps just for getting a git hash.

ant \
    -Dcheckstyle.enabled=false \
    -Drepository-info.revision=%{commit} \
    -Drepository-info.revision-number=-1 \
    -Drepository-info.type=git \
    -Drepository-info.url=https://github.com/pingidentity/ldapsdk.git \
    -Depository-info.path=\/ \
    -f build.xml package

%install

%jar -xf build/package/%{name}-%{version}-maven.jar
rm -fr META-INF
mkdir javadoc
cd javadoc
%jar -xf ../unboundid-ldapsdk-*-javadoc.jar
rm -fr META-INF
cd ..

%mvn_artifact %{name}-%{version}.pom %{name}-%{version}.jar
%mvn_file com.unboundid:%{name} %{name}
%mvn_install -J javadoc

%files -f .mfiles
%license dist-root/LICENSE.txt
%license dist-root/LICENSE-LGPLv2.1.txt
%license dist-root/LICENSE-UnboundID-LDAPSDK.txt
%license dist-root/LICENSE-GPLv2.txt
%doc dist-root/README.txt

%files javadoc -f .mfiles-javadoc
%license dist-root/LICENSE.txt
%license dist-root/LICENSE-LGPLv2.1.txt
%license dist-root/LICENSE-UnboundID-LDAPSDK.txt
%license dist-root/LICENSE-GPLv2.txt

%changelog
* Mon Jan 13 2020 Sandro Bonazzola <sbonazzo@redhat.com> - 4.0.14-2
- Add support for el8 within spec file

* Fri Jan 10 2020 Sandro Bonazzola <sbonazzo@redhat.com> - 4.0.14-1
- Update to 4.0.14 (#1783206)

* Thu Nov 28 2019 Sandro Bonazzola <sbonazzo@redhat.com> - 4.0.13-1
- Update to 4.0.13 (#1776564)

* Thu Oct 10 2019 Sandro Bonazzola <sbonazzo@redhat.com> - 4.0.12-1
- Update to 4.0.12 (#1760153)

* Sat Jul 27 2019 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Tue Jun 04 2019 Fedora Release Monitoring <release-monitoring@fedoraproject.org> - 4.0.11-1
- Update to 4.0.11 (#1717154)

* Mon Mar 11 2019 Sandro Bonazzola <sbonazzo@redhat.com> - 4.0.10-1
- Update to 4.0.10 (#1687030)

* Fri Mar 01 2019 Sandro Bonazzola <sbonazzo@redhat.com> - 4.0.9-1
- Update to 4.0.9 (#1680579)

* Sun Feb 03 2019 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Aug 07 2018 Sandro Bonazzola <sbonazzo@redhat.com> - 4.0.7-1
- Update to 4.0.7 (#1613079)

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue May 22 2018 Sandro Bonazzola <sbonazzo@redhat.com> - 4.0.6-1
- Update to 4.0.6 (#1580993)

* Mon Mar 19 2018 Sandro Bonazzola <sbonazzo@redhat.com> - 4.0.5-1
- Update to 4.0.5 (#1557972)
- Fix CVE-2018-1000134 (#1557532)

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Jan 23 2018 Fedora Release Monitoring  <release-monitoring@fedoraproject.org> - 4.0.4-1
- Update to 4.0.4 (#1537503)

* Wed Sep 06 2017 Fedora Release Monitoring  <release-monitoring@fedoraproject.org> - 4.0.1-1
- Update to 4.0.1 (#1488680)

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jun 15 2017 Sandro Bonazzola <sbonazzo@redhat.com> - 4.0.0-1
- Rebased on upstream 4.0.0
- Resolves: BZ#1461604

* Tue Mar 07 2017 Sandro Bonazzola <sbonazzo@redhat.com> - 3.2.1-1
- Rebased on upstream 3.2.1
- Resolves: BZ#1429722

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.2.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Sep 23 2016 Sandro Bonazzola <sbonazzo@redhat.com> - 3.2.0-1
- Rebased on upstream 3.2.0
- Resolves: BZ#1378924

* Tue Mar 29 2016 Sandro Bonazzola <sbonazzo@redhat.com> - 3.1.1-1
- Rebased on upstream 3.1.1

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Jun 11 2015 Sandro Bonazzola <sbonazzo@redhat.com> - 3.0.0-1
- Rebased on upstream 3.0.0
- Resolves: BZ#1230454

* Wed Apr 22 2015 Sandro Bonazzola <sbonazzo@redhat.com> - 2.3.8-4
- Fixed license as per Fedora Legal review

* Mon Apr 20 2015 Sandro Bonazzola <sbonazzo@redhat.com> - 2.3.8-3
- added unboundid-ldapsdk-2.3.8-javadoc patch from Gil Cattaneo <puntogil@libero.it>
  fixing javadoc errors

* Tue Apr 14 2015 Gil Cattaneo <puntogil@libero.it> - 2.3.8-2
- removed ant and checkstyle from tarball
- use xz for compression
- move to javac source/target 1.6
- use jdk tools instead of zip jdk
- use {javapackages,maven}-local for installing artifacts

* Mon Apr 13 2015 Sandro Bonazzola <sbonazzo@redhat.com> - 2.3.8-1
- Initial packaging

