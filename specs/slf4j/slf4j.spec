Name:		slf4j
Version:	1.7.7
Release:	1%{?release_suffix}%{?dist}
License:	MIT and ASL 2.0
Summary:	slf4j
URL:		http://www.slf4j.org/
BuildArch:	noarch
Source:		http://www.slf4j.org/dist/%{name}-%{version}.tar.gz

BuildRequires:	java-1.7.0-openjdk-devel

%description
slf4j logging library.

%prep
%setup -q
find . -name '*.jar' -exec rm {} \;
sed -i '/<module>integration<\/module>/d' pom.xml

%build
mvn -PskipTests clean install

%install
install -d -m 755 "%{buildroot}%{_javadir}/%{name}"
for name in \
		slf4j-api \
		slf4j-ext \
		slf4j-jdk14 \
		slf4j-log4j12 \
		slf4j-nop \
		slf4j-simple \
		slf4j-site \
		osgi-over-slf4j \
		log4j-over-slf4j \
		jul-to-slf4j \
		jcl-over-slf4j \
		%{nil}; do
	jar="$(find . -name "${name}-*.jar" | grep -v sources | grep -v javadoc)"
	install -p -m 644 "${jar}" "%{buildroot}%{_javadir}/%{name}/$(basename "${jar}")"
	ln -s "$(basename "${jar}")" "%{buildroot}%{_javadir}/%{name}/${name}.jar"
done

%files
%{_javadir}/%{name}/

%changelog
* Sun May 4 2014 Alon Bar-Lev <alonbl@redhat.com> 1.7.7-1
- Initial.
