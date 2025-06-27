### REF: https://www.zotero.org/support/dev/client_coding/building_the_desktop_app

Name:           zotero
Version:        7.0.19
Release:        1%{?dist}
Summary:        Zotero Reference Manager

License:        AGPL-3.0-only
URL:            https://github.com/zotero/zotero
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

ExclusiveArch:  x86_64

BuildRequires:  git nodejs rust cargo python3 gcc-c++
BuildRequires:  gtk3-devel libXt-devel libX11-devel dbus-glib-devel

Requires:       gtk3 libXt libX11 dbus-glib

%description
Zotero reference management tool built from source.

%prep
%autosetup -n %{name}-%{version}
git submodule update --init --recursive

%build
export MACH_USE_SYSTEM_PYTHON=1
./mach build

%install
mkdir -p %{buildroot}/opt/zotero %{buildroot}%{_bindir}
cp -a dist/linux64-unpacked/* %{buildroot}/opt/zotero/
ln -s /opt/zotero/zotero %{buildroot}%{_bindir}/zotero

%files
/opt/zotero
%{_bindir}/zotero

%changelog
%autochangelog
