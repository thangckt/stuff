Name:           ovito
Version:        3.12.4
Release:        1%{?dist}
Summary:        OVITO - Open Visualization Tool (GUI)

License:        MIT
URL:            https://gitlab.com/stuko/ovito
Source0:        %{url}/-/archive/v%{version}/%{name}-v%{version}.tar.gz

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
%autosetup -n %{name}-v%{version}

# Ensure file '.desktop' exists
if [ ! -f dist/linux/ovito.desktop ]; then
    echo "create file ovito.desktop"
    mkdir -p dist/linux
    cat > dist/linux/ovito.desktop << EOF
[Desktop Entry]
Name=OVITO
GenericName=Scientific Visualization Tool
Comment=Visualize and analyze atomistic simulation data
Exec=ovito
Icon=ovito
Terminal=false
Type=Application
Categories=Science;Education;Graphics;
EOF
fi

%build
mkdir -p build
cd build
cmake -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  ..
cmake --build . -- -j%{?_smp_build_ncpus}

%install
cd build
cmake --install . --prefix %{buildroot}%{_prefix}

# Install .desktop file
install -D -m 0644 ../dist/linux/ovito.desktop %{buildroot}%{_datadir}/applications/ovito.desktop

# Remove unwanted files
rm -f %{buildroot}%{_bindir}/ssh_askpass

%files
%{_bindir}/ovito
%{_datadir}/applications/ovito.desktop
%{_prefix}/lib/ovito/
%{_datadir}/ovito/

%changelog
%autochangelog