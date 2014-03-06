%global __jar_repack 0

Name:		jasperreports-server
Version:	5.5.0
Release:	8%{?dist}
License:	AGPLv3
Summary:	JasperReports Server
URL:		http://community.jaspersoft.com
BuildArch:	noarch
Source:		http://downloads.sourceforge.net/project/jasperserver/JasperServer/JasperReports%20Server%20Community%20Edition%20%{version}/%{name}-cp-%{version}-bin.zip
Patch0:		jasperreports-server-5.5.0-additional-config.patch
Patch1:		jasperreports-server-5.5.0-install_resources.patch
Patch2:		jasperreports-server-5.5.0-write-own.patch
Patch3:		jasperreports-server-5.5.0-ANT_OPTS.patch
Patch4:		jasperreports-server-5.5.0-java.io.tmpdir.patch

AutoReqProv:	no
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
%patch0 -p2 -d jasperreports-server*
%patch1 -p2 -d jasperreports-server*
%patch2 -p2 -d jasperreports-server*
%patch3 -p2 -d jasperreports-server*
%patch4 -p2 -d jasperreports-server*

%build
#
# here we remove orig files resulting of
# patching the package.
#
find . -name '*.orig' -exec rm -f {} \;

%install
install -d "%{buildroot}%{_datadir}/%{name}"

#
# must use cp -r and preserve timestamp
# as jasper tries to overwrite its own
# files, ant protects that if timestamp
# is the same.
#
cp -r jasperreports-server*/* "%{buildroot}%{_datadir}/%{name}"

#
# jasper provide plain zip, bad for attributes
#
find "%{buildroot}%{_datadir}/%{name}" -type d -exec chmod 0755 {} +
find "%{buildroot}%{_datadir}/%{name}" -type f -exec chmod 0644 {} +
chmod a+x "%{buildroot}%{_datadir}/%{name}/apache-ant/bin/ant"
chmod a+x "%{buildroot}%{_datadir}/%{name}/buildomatic/js-ant"
chmod a+x "%{buildroot}%{_datadir}/%{name}/buildomatic"/*.sh
chmod a+x "%{buildroot}%{_datadir}/%{name}/buildomatic/bin"/*.sh

%files
%defattr(-,root,root,-)
%{_datadir}/%{name}

%changelog
* Tue Mar 11 2014 Alon Bar-Lev <alonbl@redhat.com> - 5.5.0-8
- added removal of patch orig files at build time.

* Wed Feb 5 2014 Alon Bar-Lev <alonbl@redhat.com> - 5.5.0-7
- Set correct file attributes.
- Remove java build dependency.
- Make it easier to use the commercial version.

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
