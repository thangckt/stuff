### ref: https://github.com/fedora-riscv/rssguard/blob/main/rssguard.spec

Name:           rssguard
Version:        4.8.5
Release:        %autorelease
Summary:        Simple yet powerful feed reader

# GPL-3.0-or-later: main program
# BSD-3-Clause:  src/network-web/librssguard/googlesuggest.*
License:        GPL-3.0-or-later AND BSD-3-Clause
URL:            https://github.com/martinrotter/rssguard
Source0:        %{url}/archive/%{version}/%{name}-%{version}.tar.gz

ExclusiveArch:  %{qt6_qtwebengine_arches}

BuildRequires:  make
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qttools-devel
BuildRequires:  qt6-qtwebengine-devel
BuildRequires:  qt6-qtwebchannel-devel
BuildRequires:  qt6-qt5compat-devel
BuildRequires:  qt6-linguist
BuildRequires:  libappstream-glib
BuildRequires:  desktop-file-utils

Requires:       hicolor-icon-theme

%description
RSS Guard is simple, light and easy-to-use RSS/ATOM feed aggregator developed
using the Qt framework which supports online feed synchronization.

%prep
%autosetup -p1 -n %{name}-%{version}
sed -i 's/\r$//' README.md

%build
%cmake -DQT_MAJOR_VERSION=6
%cmake_build

%install
%cmake_install

%check
desktop-file-validate %{buildroot}/%{_datadir}/applications/*.desktop
appstream-util validate-relax --nonet %{buildroot}/%{_datadir}/metainfo/*.xml

%files
%doc README.md
%license LICENSE.md
%{_bindir}/%{name}
%{_datadir}/applications/io.github.martinrotter.rssguard.desktop
%{_datadir}/icons/hicolor/*/apps/io.github.martinrotter.rssguard.png
%{_datadir}/metainfo/io.github.martinrotter.rssguard.metainfo.xml

%changelog
%autochangelog