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

BuildRequires: gcc-c++ cmake gtk3-devel webkit2gtk4.1-devel
BuildRequires: pkgconfig(glib-2.0) pkgconfig(zlib) pkgconfig(expat)

%description
wxWidgets is a free and open-source C++ library for creating cross-platform graphical user interfaces (GUIs).
This package provides version 3.3.1 with GTK3 and WebKit2GTK support.

%prep
%setup -q -n wxWidgets-%{version}

%build
%cmake -DwxBUILD_SHARED=ON \
       -DwxBUILD_MONOLITHIC=OFF \
       -DwxBUILD_TOOLKIT=gtk3 \
       -DwxUSE_WEBVIEW=ON \
       -DwxUSE_WEBVIEW_WEBKIT=ON \
       -DwxUSE_WEBVIEW_EDGE=OFF \
       -DwxUSE_WEBVIEW_IE=OFF \
       -DwxUSE_RPATH=OFF \
       -DCMAKE_INSTALL_LIBDIR=%{_libdir}
%cmake_build

%install
rm -rf %{buildroot}
%cmake_install


%files
%license docs/licence.txt

# Binaries and config tools
%{_bindir}/wx-config
%{_bindir}/wxrc*

# Libraries
%{_libdir}/libwx_*.so.*
%{_libdir}/libwx_*.so
%{_includedir}/wx-3.3/
%{_libdir}/wx/
%{_libdir}/pkgconfig/wx*.pc

# Other files
%{_datadir}/locale/*/LC_MESSAGES/wxstd-3.3.mo
%{_datadir}/aclocal/wxwin.m4
%{_datadir}/bakefile/

%changelog
%autochangelog