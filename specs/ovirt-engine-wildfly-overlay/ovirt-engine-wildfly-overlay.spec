Name:		ovirt-engine-wildfly-overlay
Version:	001
Release:	1%{?dist}
Summary:	Wildfly overlay for ovirt-engine
Group:		Virtualization/Management
License:	ASL-2.0
URL:		http://www.ovirt.org
BuildArch:	noarch
Source0:	https://repo1.maven.org/maven2/org/hibernate/hibernate-validator/5.2.0.Beta1/hibernate-validator-5.2.0.Beta1.jar
Source1:	https://repo1.maven.org/maven2/org/hibernate/hibernate-validator-cdi/5.2.0.Beta1/hibernate-validator-cdi-5.2.0.Beta1.jar
Source2:	hibernate-validator-module.xml
Source3:	hibernate-validator-cdi-module.xml

%description
Wildfly overlay for ovirt-engine

%install
install -d -m 0755 "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/main"
install -m 0644 "%{SOURCE0}" "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/main/hibernate-validator.jar"
install -m 0644 "%{SOURCE2}" "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/main/module.xml"
install -d -m 0755 "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/cdi/main"
install -m 0644 "%{SOURCE1}" "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/cdi/main/hibernate-validator-cdi.jar"
install -m 0644 "%{SOURCE3}" "%{buildroot}%{_datadir}/%{name}/modules/org/hibernate/validator/cdi/main/module.xml"

%files
%{_datadir}/%{name}/

%changelog
* Thu May 14 2015 Alon Bar-Lev <alonbl@redhat.com> 001-1
- Initial.
