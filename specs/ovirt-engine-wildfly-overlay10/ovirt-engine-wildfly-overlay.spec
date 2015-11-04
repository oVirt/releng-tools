Name:		ovirt-engine-wildfly-overlay
Version:	10.0.0
Release:	1%{?dist}
Summary:	WildFly 10 overlay for ovirt-engine
Group:		Virtualization/Management
License:	ASL-2.0
URL:		http://www.ovirt.org
BuildArch:	noarch
Source0:	README.md

%description
WildFly 10 overlay for ovirt-engine

%install
install -d -m 0755 "%{buildroot}%{_docdir}/%{name}"
install -m 0644 "%{SOURCE0}" "%{buildroot}%{_docdir}/%{name}/README.md"
install -d -m 0755 "%{buildroot}%{_datadir}/%{name}/modules"

%files
%{_datadir}/%{name}/
%{_docdir}/%{name}/

%changelog
* Wed Nov 04 2015 Martin Perina <mperina@redhat.com> 10.0.0-1
- Initial release for WildFly 10
