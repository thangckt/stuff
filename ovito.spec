### REF: https://www.ovito.org/docs/current/development/build_linux.html

Name:           ovito
Version:        3.13.0
Release:        1%{?dist}
Summary:        OVITO - Open Visualization Tool (GUI)

License:        MIT
URL:            https://gitlab.com/stuko/ovito
Source0:        %{url}/-/archive/v%{version}/%{name}-v%{version}.tar.gz
Source1:        %{url}/-/raw/master/doc/manual/images/team/ovito_logo_128.png

BuildRequires:  cmake ninja-build gcc-c++
BuildRequires:  qt6-qtbase-devel qt6-qtsvg-devel
BuildRequires:  boost-devel netcdf-devel libssh-devel
BuildRequires:  python3-sphinx python3-sphinx_rtd_theme python3-devel

Requires:       qt6-qtbase qt6-qtsvg boost netcdf libssh

%description
OVITO is a scientific data visualization and analysis software for atomistic, molecular and other particle-based simulations.

%prep
%autosetup -n %{name}-v%{version}

%build
%cmake -DCMAKE_BUILD_TYPE=Release -DOVITO_BUILD_DOCS=ON -DCMAKE_CXX_FLAGS="-O3"
%cmake_build -j$(nproc)

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