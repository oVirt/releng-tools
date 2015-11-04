Name:		ovirt-engine-wildfly-overlay
Version:	8.0.4
Release:	1%{?dist}
Summary:	WildFly 8 overlay for ovirt-engine
Group:		Virtualization/Management
License:	ASL-2.0
URL:		http://www.ovirt.org
BuildArch:	noarch
Source0:	README.md
Source1:	http://central.maven.org/maven2/org/hibernate/hibernate-validator/5.2.2.Final/hibernate-validator-5.2.2.Final.jar
Source2:	hibernate-validator-module.xml
Source3:	http://central.maven.org/maven2/org/hibernate/hibernate-validator-cdi/5.2.2.Final/hibernate-validator-cdi-5.2.2.Final.jar
Source4:	hibernate-validator-cdi-module.xml

%description
WildFly 8 overlay for ovirt-engine

%install
install -d -m 0755 "%{buildroot}%{_docdir}/%{name}"
install -m 0644 "%{SOURCE0}" "%{buildroot}%{_docdir}/%{name}/README.md"
install -d -m 0755 "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/main"
install -m 0644 "%{SOURCE1}" "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/main/hibernate-validator.jar"
install -m 0644 "%{SOURCE2}" "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/main/module.xml"
install -d -m 0755 "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/cdi/main"
install -m 0644 "%{SOURCE3}" "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/cdi/main/hibernate-validator-cdi.jar"
install -m 0644 "%{SOURCE4}" "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/cdi/main/module.xml"

%files
%{_datadir}/%{name}/
%{_docdir}/%{name}/

%changelog
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
