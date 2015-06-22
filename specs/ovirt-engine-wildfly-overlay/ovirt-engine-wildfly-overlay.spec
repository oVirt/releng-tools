Name:		ovirt-engine-wildfly-overlay
Version:	001
Release:	2%{?dist}
Summary:	Wildfly overlay for ovirt-engine
Group:		Virtualization/Management
License:	ASL-2.0
URL:		http://www.ovirt.org
BuildArch:	noarch
Source0:	README.md
Source1:	http://central.maven.org/maven2/org/hibernate/hibernate-validator/5.2.0.CR1/hibernate-validator-5.2.0.CR1.jar
Source2:	hibernate-validator-module.xml
Source3:	http://central.maven.org/maven2/org/hibernate/hibernate-validator-cdi/5.2.0.CR1/hibernate-validator-cdi-5.2.0.CR1.jar
Source4:	hibernate-validator-cdi-module.xml
Source5:	http://central.maven.org/maven2/io/undertow/undertow-core/1.1.5.Final/undertow-core-1.1.5.Final.jar
Source6:	undertow-core-module.xml
Source7:	http://central.maven.org/maven2/io/undertow/undertow-servlet/1.1.5.Final/undertow-servlet-1.1.5.Final.jar
Source8:	undertow-servlet-module.xml
Source9:	http://central.maven.org/maven2/io/undertow/undertow-websockets-jsr/1.1.5.Final/undertow-websockets-jsr-1.1.5.Final.jar
Source10:	undertow-websockets-jsr-module.xml

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
install -d -m 0755 "%{buildroot}%{_datadir}/%{name}/modules/io/undertow/core/main"
install -m 0644 "%{SOURCE5}" "%{buildroot}%{_datadir}/%{name}/modules/io/undertow/core/main/undertow-core.jar"
install -m 0644 "%{SOURCE6}" "%{buildroot}%{_datadir}/%{name}/modules/io/undertow/core/main/module.xml"
install -d -m 0755 "%{buildroot}%{_datadir}/%{name}/modules/io/undertow/servlet/main"
install -m 0644 "%{SOURCE7}" "%{buildroot}%{_datadir}/%{name}/modules/io/undertow/servlet/main/undertow-servlet.jar"
install -m 0644 "%{SOURCE8}" "%{buildroot}%{_datadir}/%{name}/modules/io/undertow/servlet/main/module.xml"
install -d -m 0755 "%{buildroot}%{_datadir}/%{name}/modules/io/undertow/websocket/main"
install -m 0644 "%{SOURCE9}" "%{buildroot}%{_datadir}/%{name}/modules/io/undertow/websocket/main/undertow-websockets-jsr.jar"
install -m 0644 "%{SOURCE10}" "%{buildroot}%{_datadir}/%{name}/modules/io/undertow/websocket/main/module.xml"

%files
%{_datadir}/%{name}/
%{_docdir}/%{name}/

%changelog
* Mon Jun 22 2015 Martin Perina <mperina@redhat.com> 001-2
- Upgrade to Hibernate Validator 5.2.0.CR1 and Undertow 1.1.5.

* Thu May 14 2015 Alon Bar-Lev <alonbl@redhat.com> 001-1
- Initial.
