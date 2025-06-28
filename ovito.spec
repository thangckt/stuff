### REF: https://www.ovito.org/docs/current/development/build_linux.html

Name:           ovito
Version:        3.12.4
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
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

# Install .desktop file
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop << 'EOF'
[Desktop Entry]
Name=OVITO
GenericName=Scientific Visualization Tool
Comment=Visualize and analyze atomistic simulation data
Exec=ovito
Icon=ovito
Type=Application
Terminal=false
Categories=Science;Education;Graphics;
EOF

# Copy icon (since it is not included in the source)
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/128x128/apps
cp %{SOURCE1} %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/ovito.png

# Clean up
rm -f %{buildroot}%{_bindir}/ssh_askpass

%files
%{_bindir}/ovito
%{_datadir}/ovito/
%{_datadir}/applications/ovito.desktop
%{_datadir}/icons/hicolor/128x128/apps/ovito.png
%{_prefix}/lib/ovito/

%changelog
%autochangelog