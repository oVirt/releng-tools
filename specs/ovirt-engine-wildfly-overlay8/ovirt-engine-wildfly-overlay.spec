Name:		ovirt-engine-wildfly-overlay
Version:	8.0.5
Release:	1%{?dist}
Summary:	WildFly 8 overlay for ovirt-engine
Group:		Virtualization/Management
License:	ASL-2.0, LGPL 2.1
URL:		http://www.ovirt.org
BuildArch:	noarch
Source0:	README.md
Source1:	LICENSE.txt
Source2:	LICENSE-ASL20.txt
Source3:	LICENSE-LGPL21.txt
Source4:	http://central.maven.org/maven2/org/hibernate/hibernate-validator/5.2.2.Final/hibernate-validator-5.2.2.Final.jar
Source5:	hibernate-validator-module.xml
Source6:	http://central.maven.org/maven2/org/hibernate/hibernate-validator-cdi/5.2.2.Final/hibernate-validator-cdi-5.2.2.Final.jar
Source7:	hibernate-validator-cdi-module.xml
Source8:	http://central.maven.org/maven2/commons-collections/commons-collections/3.2.2/commons-collections-3.2.2.jar
Source9:	apache-commons-collections-module.xml

%description
WildFly 8 overlay for ovirt-engine

%install
install -d -m 0755 "%{buildroot}%{_docdir}/%{name}"
install -m 0644 "%{SOURCE0}" "%{buildroot}%{_docdir}/%{name}/README.md"
install -m 0644 "%{SOURCE1}" "%{buildroot}%{_docdir}/%{name}/LICENSE.txt"
install -m 0644 "%{SOURCE2}" "%{buildroot}%{_docdir}/%{name}/LICENSE-ASL20.txt"
install -m 0644 "%{SOURCE3}" "%{buildroot}%{_docdir}/%{name}/LICENSE-LGPL21.txt"
install -d -m 0755 "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/main"
install -m 0644 "%{SOURCE4}" "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/main/hibernate-validator.jar"
install -m 0644 "%{SOURCE5}" "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/main/module.xml"
install -d -m 0755 "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/cdi/main"
install -m 0644 "%{SOURCE6}" "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/cdi/main/hibernate-validator-cdi.jar"
install -m 0644 "%{SOURCE7}" "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/cdi/main/module.xml"
install -d -m 0755 "%{buildroot}%{_datadir}/%{name}/modules/org/apache/commons/collections/main"
install -m 0644 "%{SOURCE8}" "%{buildroot}%{_datadir}/%{name}/modules/org/apache/commons/collections/main/commons-collections.jar"
install -m 0644 "%{SOURCE9}" "%{buildroot}%{_datadir}/%{name}/modules/org/apache/commons/collections/main/module.xml"

%files
%{_datadir}/%{name}/
%{_docdir}/%{name}/

%changelog
* Wed Mar 09 2016 Martin Perina <mperina@redhat.com> 8.0.5-1
- Add proper license files
- Upgrade apache-commons-collections to version 3.2.2 to fix security issue
  https://issues.apache.org/jira/browse/COLLECTIONS-580

* Wed Nov 04 2015 Martin Perina <mperina@redhat.com> 8.0.4-1
- Change package version to be able to distinguish overlay packages
  for WildFly 8 and WildFly 10 which are incompatible

- Fix upgraded packages to match requirements for WildFly 8.2.1
- Upgrade to Hibernate Validator 5.2.2.
* Thu Oct 22 2015 Martin Perina <mperina@redhat.com> 002-1
- Fix upgraded packages to match requirements for WildFly 8.2.1
- Upgrade to Hibernate Validator 5.2.2.

* Mon Jun 22 2015 Martin Perina <mperina@redhat.com> 001-2
- Upgrade to Hibernate Validator 5.2.0.CR1 and Undertow 1.1.5.

* Thu May 14 2015 Alon Bar-Lev <alonbl@redhat.com> 001-1
- Initial.
