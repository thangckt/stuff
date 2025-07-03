Name:           goldendict
Version:        1.5.1
Release:        1%{?dist}
Summary:        Feature-rich dictionary lookup program

License:        GPL-3.0-or-later
URL:            https://github.com/goldendict/goldendict
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

BuildRequires:  qt5-qtbase-devel qt5-qtwebkit-devel qt5-qtsvg-devel qt5-qtx11extras-devel qt5-qttools-devel qt5-qttools
BuildRequires:  qt5-qtmultimedia-devel ffmpeg-free-devel hunspell-devel zlib-devel libvorbis-devel libXtst-devel
BuildRequires:  lzo-devel bzip2-devel libao-devel libtiff-devel gcc-c++ make pkgconfig git
Requires:       ffmpeg-free hunspell translate-shell mpg123

%description
GoldenDict is a feature-rich dictionary lookup program supporting multiple dictionary formats,
including Babylon, StarDict, Dictd, and others. It provides a modern Qt interface, support for
Wikipedia, and various offline/online resources.

%prep
# Clone the repository with submodules
git clone --recurse-submodules %{url}.git goldendict-%{version}
cd goldendict-%{version}
git tag
git checkout %{version}
git submodule update --init --recursive

# patch to remove 'help' from the command line options
sed -i 's/ help//' goldendict.pro

# Move source to expected build directory root
cd ..
rsync -a goldendict-%{version}/ ./
rm -rf goldendict-%{version}

%build
# Use Qt5 qmake
qmake-qt5 goldendict.pro CONFIG+=release
make -j%{?_smp_build_ncpus}

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/128x128/apps

# Install binary
install -m 0755 goldendict %{buildroot}%{_bindir}/goldendict

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
cp icons/programicon.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/goldendict.png

%files
%{_bindir}/goldendict
%{_datadir}/applications/goldendict.desktop
%{_datadir}/icons/hicolor/64x64/apps/goldendict.png

%changelog
%autochangelog
