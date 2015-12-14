%global gem_name libxml-ruby

Name: rubygem-libxml-ruby
Summary: Ruby language bindings for GNOME's Libxml2 XML toolkit.
Version: 2.8.0
Release: 1.ovirt%{?dist}
Group: Development/Languages
License: MIT
URL: http://xml4r.github.io/libxml-ruby
Source: https://rubygems.org/downloads/%{gem_name}-%{version}.gem

BuildRequires: gcc
BuildRequires: libxml2-devel
BuildRequires: ruby-devel
BuildRequires: rubygems-devel

%description
The libxml gem provides Ruby language bindings for GNOME's Libxml2 XML
toolkit.

%package doc
Summary: Documentation for %{name}
Group: Documentation
Requires: %{name} = %{version}-%{release}

%description doc
This package contains documentation for %{name}.

%prep

# Unpack the gem:
gem unpack %{SOURCE0}
%setup -q -D -T -n %{gem_name}-%{version}

%build

# Build the gem:
gem build %{gem_name}.gemspec
%gem_install

# Remove things that we don't want to package:
pushd ./%{gem_dir}
  rm -rf cache
popd
pushd ./%{gem_instdir}
  rm -rf Rakefile
  rm -rf ext
  rm -rf script
  rm -rf setup.rb
  rm -rf test
popd

%install

# Install the files:
mkdir -p %{buildroot}%{gem_dir}
cp -a ./%{gem_dir}/* %{buildroot}%{gem_dir}/

# Install the extensions:
%if 0%{?fedora} >= 21
mkdir -p %{buildroot}%{gem_extdir_mri}
cp -a ./%{gem_extdir_mri}/* %{buildroot}%{gem_extdir_mri}/
pushd %{buildroot}%{gem_extdir_mri}
  rm -f gem_make.out
  rm -f mkmf.log
popd
%else
mkdir -p %{buildroot}%{gem_extdir_mri}/lib
mv %{buildroot}%{gem_instdir}/lib/*.so %{buildroot}%{gem_extdir_mri}/lib/
%endif

%files
%doc %{gem_instdir}/HISTORY
%doc %{gem_instdir}/README.rdoc
%exclude %{gem_dir}/doc/
%license %{gem_instdir}/LICENSE
%{gem_dir}/specifications/%{gem_name}-%{version}.gemspec
%{gem_extdir_mri}/
%{gem_instdir}/

%files doc
%{gem_dir}/doc/%{gem_name}-%{version}/

%changelog
* Mon Dec 14 2015 Juan Hernandez <juan.hernandez@redhat.com> - 2.8.0-1
- Initial packaging.
