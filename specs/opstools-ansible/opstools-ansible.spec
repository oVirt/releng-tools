%global commit0 d9cd7764203255869d41be524af9e98e54a7b2ad
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global checkout 20161020git%{shortcommit0}

Name:           opstools-ansible
Version:        0.0.1
Release:        0.%{checkout}%{?dist}
Summary:        Ansible playbooks for installing OpenStack operational tools

License:        ASL 2.0
URL:            https://github.com/centos-opstools
Source0:        https://github.com/centos-opstools/%{name}/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

BuildArch:      noarch

%description
Ansible playbooks for installing OpenStack operational tools

%prep
%autosetup -n %{name}-%{commit0}

%build
# Nothing to build

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_datadir}/%{name}/group_vars
install -d %{buildroot}%{_datadir}/%{name}/inventory
install -d %{buildroot}%{_datadir}/%{name}/roles
install -p -m 644 ansible.cfg %{buildroot}%{_datadir}/%{name}/ansible.cfg
install -p -m 644 playbook.yml %{buildroot}%{_datadir}/%{name}/playbook.yml
cp -pr group_vars/* %{buildroot}%{_datadir}/%{name}/group_vars
cp -pr inventory/* %{buildroot}%{_datadir}/%{name}/inventory
cp -pr roles/* %{buildroot}%{_datadir}/%{name}/roles
# check disabled since it requires a sdist tarball or git access


%files
%license LICENSE.txt
%doc README.md
%{_datadir}/%{name}/

%changelog
* Tue Oct 11 2016 Sandro Bonazzola <sbonazzo@redhat.com> - 0.0.1-0.20161013gitee599e9
- Initial packaging
