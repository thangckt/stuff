Name:           goldendict
Version:        1.5.1
Release:        1%{?dist}
Summary:        Feature-rich dictionary lookup program

License:        GPL-3.0-or-later
URL:            https://github.com/goldendict/goldendict
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

BuildRequires:  cmake ninja-build gcc-c++
BuildRequires:  qt6-qtbase-devel qt6-qtsvg-devel qt6-qttools-devel
BuildRequires:  boost-devel libvorbis-devel zlib-devel libzip-devel
BuildRequires:  hunspell-devel libXtst-devel libX11-devel
BuildRequires:  ffmpeg-libs-devel libao-devel libsamplerate-devel

Requires:       qt6-qtbase qt6-qtsvg boost hunspell libvorbis

%description
GoldenDict is a feature-rich dictionary lookup program supporting multiple dictionary formats,
including Babylon, StarDict, Dictd, and others. It provides a modern Qt interface, support for
Wikipedia, and various offline/online resources.

%prep
%autosetup -n %{name}-%{version}

%build
%cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DUSE_QT6=ON
%cmake_build

%install
%cmake_install

# Install .desktop file
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop << 'EOF'
[Desktop Entry]
Name=GoldenDict
GenericName=Multiformat Dictionary
Exec=goldendict
Icon=goldendict
Terminal=false
Type=Application
Categories=Education;Languages;
EOF

# Install icon manually (SVG preferred if available)
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/64x64/apps
cp desktop/goldendict.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/goldendict.png

%files
%{_bindir}/goldendict
%{_datadir}/applications/goldendict.desktop
%{_datadir}/icons/hicolor/64x64/apps/goldendict.png
%license COPYING

%changelog
%autochangelog
