Name:           ovito
Version:        3.12.4
Release:        1%{?dist}
Summary:        OVITO - Open Visualization Tool (GUI)

License:        MIT
URL:            https://gitlab.com/stuko/ovito
# Source0:        %{url}/-/archive/v%{version}/%{name}-v%{version}.tar.gz
Source0:        https://gitlab.com/stuko/ovito/-/archive/master/ovito-master.tar.gz

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtsvg-devel
BuildRequires:  boost-devel
BuildRequires:  netcdf-devel
BuildRequires:  libssh-devel
BuildRequires:  python3-sphinx
BuildRequires:  python3-sphinx_rtd_theme
BuildRequires:  python3-devel

Requires:       qt6-qtbase
Requires:       qt6-qtsvg
Requires:       boost
Requires:       netcdf
Requires:       libssh

%description
OVITO is a scientific data visualization and analysis software for atomistic, molecular and other particle-based simulations. This package provides the GUI built with Qt6.

%prep
# %autosetup -n %{name}-v%{version}
%autosetup -n %{name}-master

%build
mkdir -p build
cd build
cmake -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  ..
cmake --build .

%install
cd build
cmake --install . --prefix %{buildroot}%{_prefix}

%files
%license LICENSE
%{_bindir}/ovito
%{_datadir}/applications/ovito.desktop
%{_prefix}/share/ovito/

%changelog
