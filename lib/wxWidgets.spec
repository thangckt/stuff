# Note: wxWidgets>3.3 is required for FreeFileSync. It is better to build it in another spec file.

Name:       wxWidgets
Version:    3.3.1
Release:    1%{?dist}
Summary:    A library for creating graphical user interfaces
License:    wxWidgets Library License
URL:        https://github.com/wxWidgets/wxWidgets
Source0:    %{url}/releases/download/v%{version}/wxWidgets-%{version}.tar.bz2

# Disable debug packages
%global debug_package %{nil}
%global debugsource_package %{nil}

BuildRequires: gcc-c++ cmake cmake-rpm-macros gtk3-devel webkit2gtk4.1-devel
BuildRequires: nanosvg-devel libmspack-devel xz-devel SDL3-devel
BuildRequires: pkgconfig(glib-2.0) pkgconfig(zlib) pkgconfig(expat)

%description
wxWidgets is a free and open-source C++ library for creating cross-platform graphical user interfaces (GUIs).
This package provides version 3.3.1 with GTK3 and WebKit2GTK support.

%prep
%setup -q -n wxWidgets-%{version}

%build
%cmake  -DwxBUILD_SHARED=ON \
        -DwxBUILD_MONOLITHIC=OFF \
        -DwxBUILD_TOOLKIT=gtk3 \
        -DwxUSE_WEBVIEW=ON \
        -DwxUSE_LIBLZMA=ON \
        -DwxUSE_LIBSDL=ON \
        -DwxUSE_LIBMSPACK=ON \
        -DCMAKE_INSTALL_LIBDIR=%{_libdir}
%cmake_build

%install
rm -rf %{buildroot}
%cmake_install

## Create pkgconfig directory
mkdir -p %{buildroot}%{_libdir}/pkgconfig

# Use wx-config output to create a .pc file
WX_CONFIG=%{buildroot}%{_bindir}/wx-config

$WX_CONFIG --libs > wx.libs
$WX_CONFIG --cxxflags > wx.cflags

cat > %{buildroot}%{_libdir}/pkgconfig/wxgtk3.pc <<EOF
prefix=%{_prefix}
exec_prefix=\${prefix}
libdir=%{_libdir}
includedir=\${prefix}/include/wx-3.3

Name: wxGTK3
Description: wxWidgets GUI library (GTK3 port)
Version: %version
Libs: $(cat wx.libs)
Cflags: $(cat wx.cflags)
EOF

rm -f wx.libs wx.cflags

%files
%license docs/licence.txt
%{_bindir}/wx-config
%{_bindir}/wxrc*

# Libraries
%{_libdir}/libwx_*.so.*
%{_libdir}/libwx_*.so
%{_includedir}/wx-3.3/
%{_libdir}/wx/
%{_libdir}/pkgconfig/wxgtk3.pc
%{_datadir}/locale/*

%changelog
%autochangelog