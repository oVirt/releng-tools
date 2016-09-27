%if 0%{?fedora:1}
%global _use_maven 1
%endif
%if 0%{?rhel:1}
%if %{rhel} >= 7
%global _use_maven 1
%else
%global _use_maven 0
%endif
%endif

Name:           unboundid-ldapsdk
Version:        3.2.0
Release:        1%{?dist}
Summary:        UnboundID LDAP SDK for Java

License:        GPLv2 or LGPLv2+
URL:            https://www.ldap.com/unboundid-ldap-sdk-for-java
Source0:        https://github.com/UnboundID/ldapsdk/archive/%{version}.tar.gz
BuildArch:      noarch
BuildRequires:  ant
%if 0%{?fedora}
BuildRequires:  javapackages-local
%else
%if %_use_maven
BuildRequires:  maven-local
%endif
%endif
Patch1:         unboundid-ldapsdk-3.2.0-build.patch

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
#remove external prebuilt libraries
rm -rf ext
%patch1 -p1

sed -i 's|source="1.5" target="1.5"|source="1.6" target="1.6"|' build-se.xml
sed -i 's|source="1.5"|source="1.6"|' build-se.xml
sed -i 's|target="1.5"|target="1.6"|' build-se.xml

%build
# checkstyle configuration files were in the ext directory
# code doesn't pass checkstyle 5.6 disabling the check until upstream
# fixes it
# upstream added 3rd party subversion specific code so we need to removed it
# adding -Dsvn.version=0 to ant command line as we build release we do not
# actually care what svn version is.
ant -Dcheckstyle.enabled=false -Dsvn.version=0 -f build-se.xml package

%install

%jar -xf build/package/%{name}-%{version}-maven.jar
rm -fr META-INF
mkdir javadoc
cd javadoc
%jar -xf ../unboundid-ldapsdk-*-javadoc.jar
rm -fr META-INF
cd ..

%if %_use_maven
%mvn_artifact %{name}-%{version}.pom %{name}-%{version}.jar
%mvn_file com.unboundid:%{name} %{name}
%mvn_install -J javadoc
%else
install -d -m 755 "%{buildroot}%{_javadir}"
install -p -m 644 "%{name}-%{version}.jar" "%{buildroot}%{_javadir}/%{name}.jar"
cat > .mfiles << __EOF__
%{_javadir}/%{name}.jar
__EOF__

install -d -m 755 "%{buildroot}%{_javadocdir}/%{name}"
cp -pr javadoc/* "%{buildroot}%{_javadocdir}/%{name}"
cat > .mfiles-javadoc << __EOF__
%doc %{_javadocdir}/%{name}/
__EOF__
%endif

%files -f .mfiles
%license dist-root-se/LICENSE.txt
%license dist-root-se/LICENSE-LGPLv2.1.txt
%license dist-root-se/LICENSE-UnboundID-LDAPSDK.txt
%license dist-root-se/LICENSE-GPLv2.txt
%doc dist-root-se/README.txt

%files javadoc -f .mfiles-javadoc
%license dist-root-se/LICENSE.txt
%license dist-root-se/LICENSE-LGPLv2.1.txt
%license dist-root-se/LICENSE-UnboundID-LDAPSDK.txt
%license dist-root-se/LICENSE-GPLv2.txt

%changelog
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

* Sun May 4 2014 Alon Bar-Lev <alonbl@redhat.com> 2.3.7-0.0.snap.r530
- Initial.
