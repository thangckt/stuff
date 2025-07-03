### This script just copies the original RPM file to the build directory. Should only be used for testing purposes or simple app.

Name:           rustdesk
Version:        1.4.0
Release:        1%{?dist}
Summary:        GitHub Desktop Plus

License:        GNU General Public License v3.0
URL:            https://github.com/rustdesk/rustdesk
Source0:        %{url}/releases/download/%{version}/%{name}-%{version}-0.x86_64.rpm

ExclusiveArch:  x86_64
BuildArch:      noarch
AutoReq:        no

%description
RuskDesk (prebuilt binary). This package simply copy the original RPM.

%prep
# Nothing to do

%build
# Nothing to do

%install
cp %{SOURCE0} %{_builddir}/

%files
# nothing — all files are bundled

%changelog
%autochangelog