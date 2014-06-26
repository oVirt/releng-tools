%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%global commit 30d85c9c776d8c204c66bb93e924ab8e7a92dd3b
%global shortcommit %(c=%{commit}; echo ${c:0:7})
Summary: A set of tools to gather troubleshooting information from a system
Name: sos
Version: 3.1
Release: 1.1%{?dist}.ovirt
Group: Applications/System
Source0: https://github.com/sosreport/sos/archive/%{commit}.tar.gz#/%{name}-%{commit}.tar.gz
License: GPLv2+
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch
Url: http://fedorahosted.org/sos
BuildRequires: python-devel
BuildRequires: gettext
Requires: libxml2-python
Requires: rpm-python
Requires: tar
Requires: bzip2
Requires: xz
Patch1: 0001-Fix-cluster-module-crm_report-support.patch
Patch2: 0002-Remove-obsolete-diagnostics-code-from-ldap-plugin.patch
Patch3: 0003-Ensure-superclass-postproc-method-is-called-in-ldap-.patch
Patch4: 0004-Fix-cluster-postproc-regression.patch
Patch5: 0005-Fix-get_option-use-in-cluster-plugin.patch
Patch6: 0006-Fix-verbose-file-logging.patch
Patch7: 0007-Always-treat-rhevm-vdsmlogs-option-as-string.patch
Patch8: 0008-Add-rhsm-debug-collection-to-yum-plugin.patch
Patch9: 0009-Make-get_cmd_output_now-behaviour-match-2.2.patch
Patch10: 0010-Include-geo-replication-status-in-gluster-plugin.patch
Patch11: 0011-postgresql-minor-fixes.patch
Patch12: 0012-postgresql-add-logs-about-errors-warnings.patch
Patch13: 0013-postgresql-added-license-and-copyright.patch
Patch14: 0014-postgresql-allow-use-TCP-socket.patch
Patch15: 0015-Pass-no-archive-to-rhsm-debug-script.patch
Patch16: 0016-Ensure-unused-fds-are-closed-when-calling-subprocess.patch
Patch17: 0017-Fix-gluster-volume-name-extraction.patch
Patch18: 0018-Add-distupgrade-plugin.patch
Patch19: 0019-Fix-command-output-substitution-exception.patch
Patch20: 0020-Improve-error-message-when-cluster.crm_from-is-inval.patch
Patch21: 0021-Remove-useless-check_enabled-from-sar-plugin.patch
Patch22: 0022-Eliminate-hard-coded-var-log-sa-paths-in-sar-plugin.patch
Patch23: 0023-Scrub-ldap_default_authtok-password-in-sssd-plugin.patch
Patch24: 0024-Replace-package-check-with-file-check-in-anacron.patch
Patch25: 0025-Remove-the-rhevm-plugin.patch
Patch26: 0026-powerpc-Move-VPD-related-tool-under-common-code.patch
Patch27: 0027-Add-PowerNV-specific-debug-data.patch
Patch28: 0028-Fix-remaining-use-of-obsolete-get_cmd_dir-in-plugins.patch
Patch29: 0029-Update-systemd-support.patch
Patch30: 0030-Add-tuned-plugin.patch
Patch31: 0031-Clean-up-get_cmd_path-make_cmd_path-make_cmd_dirs-me.patch
Patch32: 0032-Fix-broken-binary-detection-in-satellite-plugin.patch
Patch33: 0033-Rename-validatePlugin-to-validate_plugin.patch
Patch34: 0034-Update-policy_tests.py-for-validate_plugin-change.patch
Patch35: 0035-Match-plugins-against-policies.patch
Patch36: 0036-Do-not-collect-isos-in-cobbler-plugin.patch
Patch37: 0037-Call-rhsm-debug-with-the-sos-switch.patch
Patch38: 0038-Fix-plugin_test-exception-on-six.PY2.patch
Patch39: 0039-Remove-profile-support.patch
Patch40: 0040-Dead-code-removal-sos_relative_path.patch
Patch41: 0041-Dead-code-removal-DirTree.patch
Patch42: 0042-Dead-code-removal-utilities.checksum.patch
Patch43: 0043-Add-vim-tags-to-all-python-source-files.patch
Patch44: 0044-Dead-code-removal-sos.plugins.common_prefix.patch
Patch45: 0045-Dead-code-removal-PluginException.patch
Patch46: 0046-Convert-infiniband-to-package-list.patch
Patch47: 0047-Replace-self.policy-.pkg_by_name-us-in-Logs-plugin.patch
Patch48: 0048-Clean-up-package-checks-in-processor-plugin.patch
Patch49: 0049-Pythonify-Plugin._path_in_pathlist.patch
Patch50: 0050-Fix-x86-arch-detection-in-processor-plugin.patch
Patch51: 0051-Refactor-Plugin.collect-pathway.patch
Patch52: 0052-Remove-obsolete-checksum-reference-from-utilities_te.patch
Patch53: 0053-Update-plugin_tests.py-to-match-new-method-names.patch
Patch54: 0054-Drop-RedHatPlugin-from-procenv.patch
Patch55: 0055-Remove-sub-parameter-from-Plugin.add_copy_spec.patch
Patch56: 0056-Remove-references-to-sub-parameter-from-plugin-tests.patch
Patch57: 0057-Use-a-set-for-Plugin.copy_paths.patch
Patch58: 0058-Update-Plugin-tests-to-treat-copy_paths-as-a-set.patch
Patch59: 0059-Add-tests-for-Plugin.add_copy_spec-add_copy_specs.patch
Patch60: 0060-Raise-a-TypeError-if-add_copy_specs-is-called-with-a.patch
Patch61: 0061-Add-collection-of-grub-configuration-for-UEFI-system.patch
Patch62: 0062-Add-Plugin.do_path_regex_sub.patch
Patch63: 0063-Make-do_path_regex_sub-honour-string-regex-arguments.patch
Patch64: 0064-Add-oVirt-plugin.patch
# sos-3.1 still uses the old call_ext_prog interface.
#Patch65: 0065-Fix-call_ext_prog-use-in-oVirt-plugin.patch
Patch66: 0066-ovirt-elide-passwords-in-iso-image-uploader.conf.patch
Patch67: 0067-ovirt-elide-passwords-in-logcollector.conf.patch
Patch68: 0068-ovirt-add-package-list-to-ovirt-plugin.patch
Patch69: 0069-Add-oVirt-Data-Warehouse-support.patch
Patch70: 0070-Add-reports-support-to-oVirt-plugin.patch
Patch71: 0071-ovirt-Add-dwh-and-reports-packages-to-plugin-package.patch
Patch72: 0072-ovirt-add-ovirt-scheduler-proxy-logs.patch
Patch73: 0073-Restore-generic-UI-preamble-text.patch
Patch74: 0074-Add-postprocessing-for-etc-fstab-passwords.patch
Patch75: 0075-Elide-bootloader-password-in-grub-plugin.patch
Patch76: 0076-Make-sure-grub-password-regex-handles-all-cases.patch
Patch77: 0077-Elide-passwords-in-grub2-plugin.patch

%description
Sos is a set of tools that gathers information about system
hardware and configuration. The information can then be used for
diagnostic purposes and debugging. Sos is commonly used to help
support technicians and developers.

%prep
%setup -qn %{name}-%{commit}
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p1
%patch16 -p1
%patch17 -p1
%patch18 -p1
%patch19 -p1
%patch20 -p1
%patch21 -p1
%patch22 -p1
%patch23 -p1
%patch24 -p1
%patch25 -p1
%patch26 -p1
%patch27 -p1
%patch28 -p1
%patch29 -p1
%patch30 -p1
%patch31 -p1
%patch32 -p1
%patch33 -p1
%patch34 -p1
%patch35 -p1
%patch36 -p1
%patch37 -p1
%patch38 -p1
%patch39 -p1
%patch40 -p1
%patch41 -p1
%patch42 -p1
%patch43 -p1
%patch44 -p1
%patch45 -p1
%patch46 -p1
%patch47 -p1
%patch48 -p1
%patch49 -p1
%patch50 -p1
%patch51 -p1
%patch52 -p1
%patch53 -p1
%patch54 -p1
%patch55 -p1
%patch56 -p1
%patch57 -p1
%patch58 -p1
%patch59 -p1
%patch61 -p1
%patch62 -p1
%patch63 -p1
%patch64 -p1
%patch66 -p1
%patch67 -p1
%patch68 -p1
%patch69 -p1
%patch70 -p1
%patch71 -p1
%patch72 -p1
%patch73 -p1
%patch74 -p1
%patch75 -p1
%patch76 -p1
%patch77 -p1

%build
make

%install
rm -rf ${RPM_BUILD_ROOT}
make DESTDIR=${RPM_BUILD_ROOT} install
%find_lang %{name} || echo 0

%clean
rm -rf ${RPM_BUILD_ROOT}

%files -f %{name}.lang
%defattr(-,root,root,-)
%{_sbindir}/sosreport
%{_datadir}/%{name}
%{python_sitelib}/*
%{_mandir}/man1/*
%{_mandir}/man5/*
%doc AUTHORS README.md LICENSE 
%config(noreplace) %{_sysconfdir}/sos.conf

%changelog
* Tue Jun 17 2014 Bryn M. Reeves <bmr@redhat.com> = 3.1-1
- Elide passwords in grub2 plugin
- Make sure grub password regex handles all cases
- Elide bootloader password in grub plugin
- Add postprocessing for /etc/fstab passwords
- Restore generic UI preamble text
- [ovirt] add ovirt-scheduler-proxy logs
- [ovirt] Add dwh and reports packages to plugin package list
- Add reports support to oVirt plugin
- Add oVirt Data Warehouse support
- [ovirt] add package list to ovirt plugin
- [ovirt] elide passwords in logcollector.conf
- [ovirt] elide passwords in {iso,image}uploader.conf
- Add oVirt plugin
- Make do_path_regex_sub() honour string regex arguments
- Add collection of grub configuration for UEFI systems
- Fix x86 arch detection in processor plugin
- Remove --profile support
- Fix plugin_test exception on six.PY2
- Call rhsm-debug with the --sos switch
- Do not collect isos in cobbler plugin
- Match plugins against policies
- Fix broken binary detection in satellite plugin
- Add tuned plugin
- Update systemd support
- Fix remaining use of obsolete 'get_cmd_dir()' in plugins
- Add PowerNV specific debug data
- powerpc: Move VPD related tool under common code
- Remove the rhevm plugin.
- Replace package check with file check in anacron
- Scrub ldap_default_authtok password in sssd plugin
- Eliminate hard-coded /var/log/sa paths in sar plugin
- Improve error message when cluster.crm_from is invalid
- Fix command output substitution exception
- Add distupgrade plugin
- Fix gluster volume name extraction
- Ensure unused fds are closed when calling subprocesses via Popen
- Pass --no-archive to rhsm-debug script
- postgresql: allow use TCP socket
- postgresql: added license and copyright
- postgresql: add logs about errors / warnings
- postgresql: minor fixes
- Include geo-replication status in gluster plugin
- Make get_cmd_output_now() behaviour match 2.2
- Add rhsm-debug collection to yum plugin
- Always treat rhevm vdsmlogs option as string
- Fix verbose file logging
- Fix get_option() use in cluster plugin
- Fix cluster postproc regression
- Ensure superclass postproc method is called in ldap plugin
- Remove obsolete diagnostics code from ldap plugin
- Fix cluster module crm_report support
- Update to sos-3.1 upstream release

* Thu Mar 20 2014 Bryn M. Reeves <bmr@redhat.com> = 3.0-23
- Call rhsm-debug with the --sos switch

* Mon Mar 03 2014 Bryn M. Reeves <bmr@redhat.com> = 3.0-22
- Fix package check in anacron plugin

* Wed Feb 12 2014 Bryn M. Reeves <bmr@redhat.com> = 3.0-21
- Remove obsolete rhel_version() usage from yum plugin

* Tue Feb 11 2014 Bryn M. Reeves <bmr@redhat.com> = 3.0-20
- Prevent unhandled exception during command output substitution

* Mon Feb 10 2014 Bryn M. Reeves <bmr@redhat.com> = 3.0-19
- Fix generation of volume names in gluster plugin
- Add distupgrade plugin

* Tue Feb 04 2014 Bryn M. Reeves <bmr@redhat.com> = 3.0-18
- Prevent file descriptor leaks when using Popen
- Disable zip archive creation when running rhsm-debug
- Include volume geo-replication status in gluster plugin

* Mon Feb 03 2014 Bryn M. Reeves <bmr@redhat.com> = 3.0-17
- Fix get_option use in cluster plugin
- Fix debug logging to file when given '-v'
- Always treat rhevm plugin's vdsmlogs option as a string
- Run the rhsm-debug script from yum plugin

* Fri Jan 31 2014 Bryn M. Reeves <bmr@redhat.com> = 3.0-16
- Add new plugin to collect OpenHPI configuration
- Fix cluster plugin crm_report support
- Fix file postprocessing in ldap plugin
- Remove collection of anaconda-ks.cfg from general plugin

* Fri Jan 24 2014 Bryn M. Reeves <bmr@redhat.com> = 3.0-15
- Remove debug statements from logs plugin
- Make ethernet interface detection more robust
- Fix specifying multiple plugin options on the command line
- Make log and message levels match previous versions
- Log a warning message when external commands time out
- Remove --upload command line option
- Update sos UI text to match upstream

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> = 3.0-14
- Mass rebuild 2013-12-27

* Thu Nov 14 2013 Bryn M. Reeves <bmr@redhat.com> = 3.0-13
- Fix regressions introduced with --build option

* Tue Nov 12 2013 Bryn M. Reeves <bmr@redhat.com> = 3.0-12
- Fix typo in yum plug-in add_forbidden_paths
- Add krb5 plug-in and drop collection of krb5.keytab

* Fri Nov  8 2013 Bryn M. Reeves <bmr@redhat.com> = 3.0-10
- Add nfs client plug-in
- Fix traceback when sar module force-enabled

* Thu Nov  7 2013 Bryn M. Reeves <bmr@redhat.com> = 3.0-9
- Restore --build command line option
- Collect saved vmcore-dmesg.txt files
- Normalize temporary directory paths

* Tue Nov  5 2013 Bryn M. Reeves <bmr@redhat.com> = 3.0-7
- Add domainname output to NIS plug-in
- Collect /var/log/squid in squid plug-in
- Collect mountstats and mountinfo in filesys plug-in
- Add PowerPC plug-in from upstream

* Thu Oct 31 2013 Bryn M. Reeves <bmr@redhat.com> = 3.0-6
- Remove version checks in gluster plug-in
- Check for usable temporary directory
- Fix --alloptions command line option
- Fix configuration fail regression

* Wed Oct 30 2013 Bryn M. Reeves <bmr@redhat.com> = 3.0-5
- Include /etc/yaboot.conf in boot plug-in
- Fix collection of brctl output in networking plug-in
- Verify limited set of RPM packages by default
- Do not strip newlines from command output
- Limit default sar data collection

* Thu Oct 3 2013 Bryn M. Reeves <bmr@redhat.com> = 3.0-4
- Do not attempt to read RPC pseudo files in networking plug-in
- Restrict wbinfo collection to the current domain
- Add obfuscation of luci secrets to cluster plug-in
- Add XFS plug-in
- Fix policy class handling of --tmp-dir
- Do not set batch mode if stdin is not a TTY
- Attempt to continue when reading bad input in interactive mode

* Wed Aug 14 2013 Bryn M. Reeves <bmr@redhat.com> = 3.0-3
- Add crm_report support to cluster plug-in
- Fix rhel_version() usage in cluster and s390 plug-ins
- Strip trailing newline from command output

* Mon Jun 10 2013 Bryn M. Reeves <bmr@redhat.com> = 3.0-2
- Silence 'could not run' messages at default verbosity
- New upstream release

* Thu May 23 2013 Bryn M. Reeves <bmr@redhat.com> = 2.2-39
- Always invoke tar with '-f-' option

* Mon Jan 21 2013 Bryn M. Reeves <bmr@redhat.com> = 2.2-38
- Fix interactive mode regression when --ticket unspecified

* Fri Jan 18 2013 Bryn M. Reeves <bmr@redhat.com> = 2.2-37
- Fix propagation of --ticket parameter in interactive mode

* Thu Jan 17 2013 Bryn M. Reeves <bmr@redhat.com> = 2.2-36
- Revert OpenStack patch

* Wed Jan  9 2013 Bryn M. Reeves <bmr@redhat.com> = 2.2-35
- Report --name and --ticket values as defaults
- Fix device-mapper command execution logging
- Fix data collection and rename PostreSQL module to pgsql

* Fri Oct 19 2012 Bryn M. Reeves <bmr@redhat.com> = 2.2-34
- Add support for content delivery hosts to RHUI module

* Thu Oct 18 2012 Bryn M. Reeves <bmr@redhat.com> = 2.2-33
- Add Red Hat Update Infrastructure module
- Collect /proc/iomem in hardware module
- Collect subscription-manager output in general module
- Collect rhsm log files in general module
- Fix exception in gluster module on non-gluster systems
- Fix exception in psql module when dbname is not given

* Wed Oct 17 2012 Bryn M. Reeves <bmr@redhat.com> = 2.2-32
- Collect /proc/pagetypeinfo in memory module
- Strip trailing newline from command output
- Add sanlock module
- Do not collect archived accounting files in psacct module
- Call spacewalk-debug from rhn module to collect satellite data

* Mon Oct 15 2012 Bryn M. Reeves <bmr@redhat.com> = 2.2-31
- Avoid calling volume status when collecting gluster statedumps
- Use a default report name if --name is empty
- Quote tilde characters passed to shell in RPM module
- Collect KDC and named configuration in ipa module
- Sanitize hostname characters before using as report path
- Collect /etc/multipath in device-mapper module
- New plug-in for PostgreSQL
- Add OpenStack module
- Avoid deprecated sysctls in /proc/sys/net
- Fix error logging when calling external programs
- Use ip instead of ifconfig to generate network interface lists

* Wed May 23 2012 Bryn M. Reeves <bmr@redhat.com> = 2.2-29
- Collect the swift configuration directory in gluster module
- Update IPA module and related plug-ins

* Fri May 18 2012 Bryn M. Reeves <bmr@redhat.com> = 2.2-28
- Collect mcelog files in the hardware module

* Wed May 02 2012 Bryn M. Reeves <bmr@redhat.com> = 2.2-27
- Add nfs statedump collection to gluster module

* Tue May 01 2012 Bryn M. Reeves <bmr@redhat.com> = 2.2-26
- Use wildcard to match possible libvirt log paths

* Mon Apr 23 2012 Bryn M. Reeves <bmr@redhat.com> = 2.2-25
- Add forbidden paths for new location of gluster private keys

* Fri Mar  9 2012 Bryn M. Reeves <bmr@redhat.com> = 2.2-24
- Fix katello and aeolus command string syntax
- Remove stray hunk from gluster module patch

* Thu Mar  8 2012 Bryn M. Reeves <bmr@redhat.com> = 2.2-22
- Correct aeolus debug invocation in CloudForms module
- Update gluster module for gluster-3.3
- Add additional command output to gluster module
- Add support for collecting gluster configuration and logs

* Wed Mar  7 2012 Bryn M. Reeves <bmr@redhat.com> = 2.2-19
- Collect additional diagnostic information for realtime systems
- Improve sanitization of RHN user and case number in report name
- Fix verbose output and debug logging
- Add basic support for CloudForms data collection
- Add support for Subscription Asset Manager diagnostics

* Tue Mar  6 2012 Bryn M. Reeves <bmr@redhat.com> = 2.2-18
- Collect fence_virt.conf in cluster module
- Fix collection of /proc/net directory tree
- Gather output of cpufreq-info when present
- Fix brctl showstp output when bridges contain multiple interfaces
- Add /etc/modprobe.d to kernel module
- Ensure relative symlink targets are correctly handled when copying
- Fix satellite and proxy package detection in rhn plugin
- Collect stderr output from external commands
- Collect /proc/cgroups in the cgroups module
  Resolve: bz784874
- Collect /proc/irq in the kernel module
- Fix installed-rpms formatting for long package names
- Add symbolic links for truncated log files
- Collect non-standard syslog and rsyslog log files
- Use correct paths for tomcat6 in RHN module
- Obscure root password if present in anacond-ks.cfg
- Do not accept embedded forward slashes in RHN usernames
- Add new sunrpc module to collect rpcinfo for gluster systems

* Tue Nov  1 2011 Bryn M. Reeves <bmr@redhat.com> = 2.2-17
- Do not collect subscription manager keys in general plugin
 
* Fri Sep 23 2011 Bryn M. Reeves <bmr@redhat.com> = 2.2-16
- Fix execution of RHN hardware.py from hardware plugin
- Fix hardware plugin to support new lsusb path

* Fri Sep 09 2011 Bryn M. Reeves <bmr@redhat.com> = 2.2-15
- Fix brctl collection when a bridge contains no interfaces
- Fix up2dateclient path in hardware plugin

* Mon Aug 15 2011 Bryn M. Reeves <bmr@redhat.com> = 2.2-14
- Collect brctl show and showstp output
- Collect nslcd.conf in ldap plugin

* Sun Aug 14 2011 Bryn M. Reeves <bmr@redhat.com> = 2.2-11
- Truncate files that exceed specified size limit
- Add support for collecting Red Hat Subscrition Manager configuration
- Collect /etc/init on systems using upstart
- Don't strip whitespace from output of external programs
- Collect ipv6 neighbour table in network module
- Collect basic cgroups configuration data

* Sat Aug 13 2011 Bryn M. Reeves <bmr@redhat.com> = 2.2-10
- Fix collection of data from LVM2 reporting tools in devicemapper plugin
- Add /proc/vmmemctl collection to vmware plugin

* Fri Aug 12 2011 Bryn M. Reeves <bmr@redhat.com> = 2.2-9
- Collect yum repository list by default
- Add basic Infiniband plugin
- Add plugin for scsi-target-utils iSCSI target
- Fix autofs plugin LC_ALL usage
- Fix collection of lsusb and add collection of -t and -v outputs
- Extend data collection by qpidd plugin
- Add ethtool pause, coalesce and ring (-a, -c, -g) options to network plugin

* Thu Apr 07 2011 Bryn M. Reeves <bmr@redhat.com> = 2.2-8
- Use sha256 for report digest when operating in FIPS mode
 
* Tue Apr 05 2011 Bryn M. Reeves <bmr@redhat.com> = 2.2-7
- Fix parted and dumpe2fs output on s390

* Fri Feb 25 2011 Bryn M. Reeves <bmr@redhat.com> = 2.2-6
- Fix collection of chkconfig output in startup.py
- Collect /etc/dhcp in dhcp.py plugin
- Collect dmsetup ls --tree output in devicemapper.py
- Collect lsblk output in filesys.py

* Thu Feb 24 2011 Bryn M. Reeves <bmr@redhat.com> = 2.2-4
- Fix collection of logs and config files in sssd.py
- Add support for collecting entitlement certificates in rhn.py

* Thu Feb 03 2011 Bryn M. Reeves <bmr@redhat.com> = 2.2-3
- Fix cluster plugin dlm lockdump for el6
- Add sssd plugin to collect configuration and logs
- Collect /etc/anacrontab in system plugin
- Correct handling of redhat-release for el6

* Thu Jul 29 2010 Adam Stokes <ajs at redhat dot com> = 2.2-2

* Thu Jun 10 2010 Adam Stokes <ajs at redhat dot com> = 2.2-0

* Wed Apr 28 2010 Adam Stokes <ajs at redhat dot com> = 2.1-0

* Mon Apr 12 2010 Adam Stokes <ajs at redhat dot com> = 2.0-0

* Tue Mar 30 2010 Adam Stokes <ajs at redhat dot com> = 1.9-3
- fix setup.py to autocompile translations and man pages
- rebase 1.9

* Fri Mar 19 2010 Adam Stokes <ajs at redhat dot com> = 1.9-2
- updated translations

* Thu Mar 04 2010 Adam Stokes <ajs at redhat dot com> = 1.9-1
- version bump 1.9
- replaced compression utility with xz
- strip threading/multiprocessing
- simplified progress indicator
- pylint update
- put global vars in class container
- unittests
- simple profiling
- make use of xgettext as pygettext is deprecated

* Mon Jan 18 2010 Adam Stokes <ajs at redhat dot com> = 1.8-21
- more sanitizing options for log files
- rhbz fixes from RHEL version merged into trunk
- progressbar update

* Tue Nov 19 2009 Adam Stokes <ajs at redhat dot com> = 1.8-20
- dont copy unwanted files due to symlinks
- More plugin enhancements

* Tue Nov 5 2009 Adam Stokes <ajs at redhat dot com> = 1.8-18
- Option to enable selinux fixfiles check
- Start of replacing Thread module with multiprocessing
- Update translations
- More checks against conf file versus command line opts

* Tue Sep 9 2009 Adam Stokes <ajs at redhat dot com> = 1.8-16
- Update rh-upload-core to rh-upload and allows general files
- Fix cluster plugin with pwd mangling invalidating xml
- Cluster support detecting invalid fence_id and fence states
- Read variables from conf file

* Thu Jul 23 2009 Adam Stokes <ajs at redhat dot com> = 1.8-14
- resolves: rhbz512536 wrong group in spec file
- resolves: rhbz498398 A series of refactoring patches to sos
- resolves: rhbz501149 A series of refactoring patches to sos (2)
- resolves: rhbz503804 remove obsolete translation
- resolves: rhbz502455 tricking sosreport into rm -rf /
- resolves: rhbz501146 branding in fedora

* Mon Jul 20 2009 Adam Stokes <ajs at redhat dot com> = 1.8-13
- Add requirements for tar,bzip2 during minimal installs
- More merges from reports against RHEL version of plugins
- Remove unecessary definition of localdir in spec

* Wed May 05 2009 Adam Stokes <ajs at redhat dot com> - 1.8-11
- Remove all instances of sysrq
- Consistent macro usage in spec

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Dec 29 2008 Adam Stokes <ajs at redhat dot com> - 1.8-5
- removed source defines as python manifest handles this

* Fri Dec 19 2008 Adam Stokes <ajs at redhat dot com> - 1.8-4
- spec cleanup, fixed license, source
- reworked Makefile to build properly

* Thu Oct 23 2008 Adam Stokes <astokes at redhat dot com> - 1.8-1

* Wed Nov 21 2007 Navid Sheikhol-Eslami <navid at redhat dot com> - 1.8-0
- selinux: always collect sestatus
- added many languages
- added --debug option which causes exceptions not to be trapped
- updated to sysreport-1.4.3-13.el5
- ftp upload to dropbox with --upload
- cluster: major rewrite to support different versions of RHEL
- cluster: check rg_test for errors
- minor changes in various plug-ins (yum, networking, process, kernel)
- fixed some exceptions in threads which were not properly trapped
- veritas: don't run rpm -qa every time
- using rpm's python bindings instead of external binary
- corrected autofs and ldap plugin that were failing when debug option was not found in config file.
- implemented built-in checkdebug() that uses self.files and self.packages to make the decision
- missing binaries are properly detected now.
- better doExitCode handling
- fixed problem with rpm module intercepting SIGINT
- error when user specifies an invalid plugin or plugin option
- named: fixed indentation
- replaced isOptionEnabled() with getOption()
- tune2fs and fdisk were not always run against the correct devices/mountpoint
- added gpg key to package
- updated README with new svn repo and contributors
- updated manpage
- better signal handling
- caching of rpm -q outputs
- report filename includes rhnUsername if available
- report encryption via gpg and support pubkey
- autofs: removed redundant files
- filesys: better handling of removable devices
- added sosReadFile() returns a file's contents
- return after looping inside a directory
- collect udevinfo for each block device
- simply collect output of fdisk -l in one go
- handle sysreport invocation properly (warn if shell is interactive, otherwise spawn sysreport.legacy)
- progress bar don't show 100% until finished() is called
- now runs on RHEL3 as well (python 2.2)
- replaced commonPrefix() with faster code
- filesys: one fdisk -l for all
- selinux: collect fixfilex check output
- devicemapper: collect udevinfo for all block devices
- cluster: validate node names according to RFC 2181
- systemtap: cleaned up and added checkenabled() method
- added kdump plugin
- added collection of /etc/inittab

* Wed Aug 13 2007 Navid Sheikhol-Eslami <navid at redhat dot com> - 1.7-8
- added README.rh-upload-core

* Mon Aug 13 2007 Navid Sheikhol-Eslami <navid at redhat dot com> - 1.7-7
- added extras/rh-upload-core script from David Mair <dmair@redhat.com>

* Mon Aug  9 2007 Navid Sheikhol-Eslami <navid at redhat dot com> - 1.7-6
- more language fixes
- added arabic, italian and french
- package prepared for release
- included sysreport as sysreport.legacy

* Mon Aug  9 2007 Navid Sheikhol-Eslami <navid at redhat dot com> - 1.7-5
- package obsoletes sysreport and creates a link pointing to sosreport
- added some commands in cluster and process plugins
- fixed html output (wrong links to cmds, thanks streeter)
- process: back down sleep if D state doesn't change

* Mon Aug  1 2007 Navid Sheikhol-Eslami <navid at redhat dot com> - 1.7-4
- catch KeyboardInterrupt when entering sosreport name
- added color output for increased readability
- list was sorted twice, removing latter .sort()

* Mon Jul 31 2007 Navid Sheikhol-Eslami <navid at redhat dot com> - 1.7-3
- added preliminary problem diagnosis support
- better i18n initialization
- better user messages
- more progressbar fixes
- catch and log python exceptions in report
- use python native commands to create symlinks
- limit concurrent running threads

* Mon Jul 28 2007 Navid Sheikhol-Eslami <navid at redhat dot com> - 1.7-2
- initial language localization support
- added italian translation

* Mon Jul 16 2007 Navid Sheikhol-Eslami <navid at redhat dot com> - 1.7-1
- split up command outputs in sub-directories (sos_command/plugin/command instead of sos_command/plugin.command)
- fixed doExitCode() calling thread.wait() instead of join()
- curses menu is disabled by default
- multithreading is enabled by default
- major progressbar changes (now has ETA)
- multithreading fixes
- plugins class descriptions shortened to fix better in --list-plugins
- rpm -Va in plugins/rpm.py sets eta_weight to 200 (plugin 200 longer than other plugins, for ETA calculation)
- beautified command output filenames in makeCommandFilename()

* Mon Jul 12 2007 Navid Sheikhol-Eslami <navid at redhat dot com> - 1.7-0
- curses menu disabled by default (enable with -c)
- sosreport output friendlier to the user (and similar to sysreport)
- smarter plugin listing which also shows options and disable/enabled plugins
- require root permissions only for actual sosreport generation
- fix in -k where option value was treated as string instead of int
- made progressbar wider (60 chars)
- selinux plugin is enabled only if selinux is also enabled on the system
- made some errors less verbose to the user
- made sosreport not copy files pointed by symbolic links (same as sysreport, we don't need /usr/bin/X or /sbin/ifup)
- copy links as links (cp -P)
- added plugin get_description() that returns a short decription for the plugin
- guess sosreport name from system's name

* Mon Jul  5 2007 Navid Sheikhol-Eslami <navid at redhat dot com> - 1.6-5
- Yet more fixes to make package Fedora compliant.

* Mon Jul  5 2007 Navid Sheikhol-Eslami <navid at redhat dot com> - 1.6-4
- More fixes to make package Fedora compliant.

* Mon Jul  2 2007 Navid Sheikhol-Eslami <navid at redhat dot com> - 1.6-3
- Other fixes to make package Fedora compliant.

* Mon Jul  2 2007 Navid Sheikhol-Eslami <navid at redhat dot com> - 1.6-2
- Minor fixes.

* Mon Jul  2 2007 Navid Sheikhol-Eslami <navid at redhat dot com> - 1.6-1
- Beautified output of --list-plugins.
- GPL licence is now included in the package.
- added python-devel requirement for building package

* Fri May 25 2007 Steve Conklin <sconklin at redhat dot com> - 1.5-1
- Bumped version

* Fri May 25 2007 Steve Conklin <sconklin at redhat dot com> - 1.4-2
- Fixed a backtrace on nonexistent file in kernel plugin (thanks, David Robinson)

* Mon Apr 30 2007 Steve Conklin <sconklin at redhat dot com> - 1.4-1
- Fixed an error in option handling
- Forced the file generated by traceroute to not end in .com
- Fixed a problem with manpage
- Added optional traceroute collection to networking plugin
- Added clalance's patch to gather iptables info.
- Fixes to the device-mapper plugin
- Fixed a problem with installation of man page

* Mon Apr 16 2007 Steve Conklin <sconklin at redhat dot com> - 1.3-3
- including patches to fix the following:

* Tue Feb 20 2007 John Berninger <jwb at redhat dot com> - 1.3-2
- Add man page

* Fri Dec 15 2006 Steve Conklin <sconklin at redhat dot com> - 1.3-1
- really fixed bz_219654

* Fri Dec 15 2006 Steve Conklin <sconklin at redhat dot com> - 1.2-1
- fixed a build problem

* Fri Dec 15 2006 Steve Conklin <sconklin at redhat dot com> - 1.1-1
- Tighten permissions of tmp directory so only readable by creator bz_219657
- Don't print message 'Problem at path ...'  bz_219654
- Removed useless message bz_219670
- Preserve file modification times bz_219674
- Removed unneeded message about files on copyProhibitedList bz_219712

* Wed Aug 30 2006 Steve Conklin <sconklin at redhat dot com> - 1.0-1
- Seperated upstream and RPM versioning

* Mon Aug 21 2006 Steve Conklin <sconklin at redhat dot com> - 0.1-11
- Code cleanup, fixed a regression in threading

* Mon Aug 14 2006 Steve Conklin <sconklin at redhat dot com> - 0.1-10
- minor bugfixes, added miltithreading option, setup now quiet

* Mon Jul 17 2006 Steve Conklin <sconklin at redhat dot com> - 0.1-9
- migrated to svn on 108.redhat.com, fixed a problem with command output linking in report

* Mon Jun 19 2006 Steve Conklin <sconklin at redhat dot com> - 0.1-6
- Added LICENSE file containing GPL

* Wed May 31 2006 Steve Conklin <sconklin at redhat dot com> - 0.1-5
- Added fixes to network plugin and prepped for Fedora submission

* Wed May 31 2006 John Berninger <jwb at redhat dot com> - 0.1-4
- Reconsolidated subpackages into one package per discussion with sconklin

* Mon May 22 2006 John Berninger <jwb at redhat dot com> - 0.1-3
- Added ftp, ldap, mail, named, samba, squid SOS plugins
- Fixed various errors in kernel and hardware plugins

* Mon May 22 2006 John Benringer <jwb at redhat dot com> - 0.1-2
- split off cluster plugin into subpackage
- correct file payload lists

* Mon May 22 2006 John Berninger <jwb at redhat dot com> - 0.1-1
- initial package build

