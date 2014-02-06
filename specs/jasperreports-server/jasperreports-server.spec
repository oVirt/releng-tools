%global __jar_repack 0

Name:		jasperreports-server
Version:	5.5.0
Release:	6%{?dist}
License:	AGPLv3
Summary:	JasperReports Server
URL:		http://community.jaspersoft.com
BuildArch:	noarch
Source:		http://downloads.sourceforge.net/project/jasperserver/JasperServer/JasperReports%20Server%20Community%20Edition%20%{version}/%{name}-cp-%{version}-bin.zip
Patch0:		%{name}-%{version}-additional-config.patch
Patch1:		%{name}-%{version}-install_resources.patch
Patch2:		%{name}-%{version}-write-own.patch
Patch3:		%{name}-%{version}-ANT_OPTS.patch
Patch4:		%{name}-%{version}-java.io.tmpdir.patch

AutoReqProv:	no
BuildRequires:	java-1.7.0-openjdk-devel
Requires:	bash
Requires:	java

%description
JasperReports Server is a powerful, yet flexible and
lightweight reporting server. Generate, organize, secure,
and deliver interactive reports and dashboards to users.
Allow non-technical users to build their own reports and
dashboards.

%prep
%setup -c -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

%build

%install
install -d %{buildroot}%{_datadir}/%{name}
cp -r %{name}-cp-%{version}-bin/* %{buildroot}%{_datadir}/%{name}

%files
%defattr(-,root,root,-)
%{_datadir}/%{name}

%changelog
* Wed Feb 5 2014 Alon Bar-Lev <alonbl@redhat.com> - 5.5.0-6
- Make jasper respect ANT_OPTS.
- Make jasper delegate java.io.tmpdir to sub processes.

* Tue Jan 28 2014 Alon Bar-Lev <alonbl@redhat.com> - 5.5.0-5
- Prevent jasper build to modify files at /usr.

* Thu Jan 16 2014 Sandro Bonazzola <sbonazzo@redhat.com> - 5.5.0-4
- Dropped application server and db dependencies as we are just repackaging the
  Jasper .zip distribution, which is application server independent.

* Thu Jan 16 2014 Alon Bar-Lev <alonbl@redhat.com> - 5.5.0-3
- Fix bugs in jasper build system.

* Fri Dec 20 2013 Sandro Bonazzola <sbonazzo@redhat.com> - 5.5.0-2
- Fixed W: no-build-section
- Fixed W: invalid-url

* Wed Nov 13 2013 Yaniv Dary <ydary@redhat.com> - 5.5.0-1
- Update to 5.5.0.

* Tue Sep 24 2013 Yaniv Dary <ydary@redhat.com> - 5.2.0
- Update to 5.2.0.

* Sun Jun 10 2012 Yaniv Dary <ydary@redhat.com> - 4.7.0
- inital commit
