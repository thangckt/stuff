### REF: https://src.fedoraproject.org/rpms/wxGTK/blob/rawhide/f/wxGTK.spec
# Note: FreeFileSync 14.4 depends on wxWidgets=3.3.0. It is better to build it in another spec file.

Name:       wxGTK3
Version:    3.3.0
Release:    1%{?dist}
Summary:    A library for creating graphical user interfaces
License:    wxWidgets Library License
URL:        https://github.com/wxWidgets/wxWidgets
Source0:    %{url}/releases/download/v%{version}/wxWidgets-%{version}.tar.bz2
Patch0:     ../patch/wxwidgets-image-fix.patch

# Disable debug packages
%global debug_package %{nil}
%global debugsource_package %{nil}

BuildRequires: gcc-c++ cmake gtk3-devel webkit2gtk4.1-devel
BuildRequires: libtiff-devel expat-devel SDL2-devel zlib-devel libpng-devel libjpeg-devel
BuildRequires: gstreamer1-plugins-bad-free-devel libmspack-devel
BuildRequires: libsecret-devel libcurl-devel glibc-langpack-en mesa-libEGL

%description
wxWidgets is a free and open-source C++ library for creating cross-platform graphical user interfaces (GUIs).
This package provides version 3.3.1 with GTK3 and WebKit2GTK support.

%prep
%setup -q -n wxWidgets-%{version}
%patch0 -p1

%build
# Add NDEBUG to disable assertions and prevent runtime assertion failures
export CPPFLAGS="${CPPFLAGS} -DNDEBUG -DwxDEBUG_LEVEL=0"
export CXXFLAGS="${CXXFLAGS} -DNDEBUG -DwxDEBUG_LEVEL=0 -Wno-unused-but-set-variable"

%cmake  -DwxBUILD_SHARED=ON \
        -DwxBUILD_MONOLITHIC=OFF \
        -DwxBUILD_TOOLKIT=gtk3 \
        -DwxUSE_NANOSVG=sys \
        -DwxUSE_WEBVIEW=ON \
        -DwxUSE_LIBLZMA=ON \
        -DwxUSE_LIBSDL=ON \
        -DwxUSE_LIBMSPACK=ON \
        -DCMAKE_BUILD_TYPE=Release \
        -DwxUSE_DEBUG_CONTEXT=OFF \
        -DwxUSE_DEBUGREPORT=OFF
%cmake_build

%install
rm -rf %{buildroot}
%cmake_install

## Fix absolute symlinks pointing into BUILDROOT
for bin in wx-config wxrc wxrc-3.3; do
    path="%{buildroot}%{_bindir}/$bin"
    if [ -L "$path" ]; then
        target=$(readlink "$path")
        # If the target is absolute and points inside the buildroot
        if [[ "$target" = %{_prefix}* ]]; then
            rel_target=$(realpath --relative-to=$(dirname "$path") "%{buildroot}$target")
            ln -sf "$rel_target" "$path"
        fi
    fi
done

## Create pkgconfig directory
mkdir -p %{buildroot}%{_libdir}/pkgconfig

# Use wx-config output to create a .pc file
WX_CONFIG=%{buildroot}%{_bindir}/wx-config

$WX_CONFIG --libs all > wx.libs
$WX_CONFIG --cxxflags > wx.cflags

cat > %{buildroot}%{_libdir}/pkgconfig/wxgtk3.pc <<EOF
prefix=%{_prefix}
exec_prefix=\${prefix}
libdir=%{_libdir}
includedir=\${prefix}/include/wx-3.3

Name: wxGTK3
Description: wxWidgets GUI library (GTK3 port)
Version: %{version}
Libs: $(cat wx.libs)
Cflags: $(cat wx.cflags)
EOF

rm -f wx.libs wx.cflags

%files
%license docs/licence.txt
%{_bindir}/wx-config
%{_bindir}/wxrc*

# Libraries
/usr/lib/libwx_*.so.*
/usr/lib/libwx_*.so
/usr/lib/wx/
/usr/lib/cmake/
%{_includedir}/wx-3.3/
%{_libdir}/pkgconfig/wxgtk3.pc
%{_datadir}/locale/*

%changelog
%autochangelog
