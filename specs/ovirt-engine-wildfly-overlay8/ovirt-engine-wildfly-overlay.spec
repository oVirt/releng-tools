Name:		ovirt-engine-wildfly-overlay
Version:	002
Release:	1%{?dist}
Summary:	Wildfly overlay for ovirt-engine
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
Wildfly overlay for ovirt-engine

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
* Thu Oct 22 2015 Martin Perina <mperina@redhat.com> 002-1
- Fix upgraded packages to match requirements for WildFly 8.2.1
- Upgrade to Hibernate Validator 5.2.2.

* Mon Jun 22 2015 Martin Perina <mperina@redhat.com> 001-2
- Upgrade to Hibernate Validator 5.2.0.CR1 and Undertow 1.1.5.

* Thu May 14 2015 Alon Bar-Lev <alonbl@redhat.com> 001-1
- Initial.
