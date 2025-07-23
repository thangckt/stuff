### REF: https://www.ovito.org/docs/current/development/build_linux.html

Name:           pdf4qt
Version:        1.5.1.0
Release:        1%{?dist}
Summary:        PDF4QT: An open-source PDF editor

License:        LGPLv3
URL:            https://github.com/JakubMelka/PDF4QT
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

BuildRequires:  cmake ninja-build gcc-c++
BuildRequires:  qt6-qtbase-devel qt6-qtsvg-devel
BuildRequires:  boost-devel netcdf-devel libssh-devel
BuildRequires:  python3-sphinx python3-sphinx_rtd_theme python3-devel

Requires:       qt6-qtbase qt6-qtsvg boost netcdf libssh

%description
OVITO is a scientific data visualization and analysis software for atomistic, molecular and other particle-based simulations.

%prep
%autosetup -n PDF4QT-v%{version}

%build
%cmake -DPDF4QT_INSTALL_QT_DEPENDENCIES=0 -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake -DCMAKE_INSTALL_PREFIX='/' -DCMAKE_BUILD_TYPE=Release
%cmake_build -j%{?_smp_build_ncpus}

%install
%cmake_install
strip %{buildroot}%{_bindir}/ovito

# Install .desktop file
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop << 'EOF'
[Desktop Entry]
Name=OVITO
GenericName=Scientific Visualization Tool
Exec=ovito
Icon=ovito
Type=Application
Terminal=false
Categories=Science;Education;Graphics;
EOF

# Copy icon (since it is not included in the source)
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
cp %{SOURCE1} %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/ovito.png

# Install documentation
mkdir -p %{buildroot}%{_datadir}/goldendict/doc
cp -a doc/* %{buildroot}%{_datadir}/goldendict/doc/

# Clean up
rm -f %{buildroot}%{_bindir}/ssh_askpass

%files
%{_bindir}/ovito
%{_datadir}/ovito/
%{_datadir}/applications/ovito.desktop
%{_datadir}/icons/hicolor/scalable/apps/ovito.png
%{_prefix}/lib/ovito/

%changelog
%autochangelog