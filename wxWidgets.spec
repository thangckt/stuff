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

BuildRequires: gcc-c++ gtk3-devel webkit2gtk4.1-devel
BuildRequires: pkgconfig(glib-2.0) pkgconfig(zlib) pkgconfig(expat)

%description
wxWidgets is a free and open-source C++ library for creating cross-platform graphical user interfaces (GUIs).
This package provides version 3.3.1 with GTK3 and WebKit2GTK support.

%prep
%setup -q -n wxWidgets-%{version}

%build
# Perform an in-source build to simplify path handling. This avoids issues with relative paths in out-of-source builds for some make targets.
# The configure script and make will be run directly from the extracted source directory.
./configure --prefix=%{_prefix} --libdir=%{_libdir} --with-gtk=3 --enable-webview --disable-rpath
make -j$(nproc)

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install

## Remove unused libtool files
find %{buildroot} -name "*.la" -delete

%files
%license docs/licence.txt
%{_bindir}/wx-config
%{_bindir}/wxrc
%{_bindir}/wxrc-3.3
%{_libdir}/libwx_*.so.*

# Pkgconfig and headers
%{_includedir}/wx-3.3/
%{_libdir}/wx/

# Other libraries and resources
%{_datadir}/locale/*/LC_MESSAGES/wxstd-3.3.mo
%{_datadir}/aclocal/wxwin.m4
%{_datadir}/bakefile/presets/*.bkl
%{_datadir}/bakefile/presets/wx_presets.py

%changelog
%autochangelog