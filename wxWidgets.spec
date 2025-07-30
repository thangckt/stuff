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
rm -rf build
mkdir build
pushd build
../configure --prefix=%{_prefix} --with-gtk=3 --enable-webview --disable-bakefile --without-aclocaldir
make -j$(nproc)
popd

%install
rm -rf %{buildroot}
make -C build DESTDIR=%{buildroot} install

# Remove unused libtool files
find %{buildroot} -name "*.la" -delete

# Remove bakefile and aclocal stuff (if still created)
rm -rf %{buildroot}%{_datadir}/bakefile
rm -f %{buildroot}%{_datadir}/aclocal/wxwin.m4

%files
%license docs/licence.txt
%{_bindir}/wx-config
%{_libdir}/libwx_*.so.*
%{_libdir}/pkgconfig/wx*.pc
%{_includedir}/wx-3.3/
%{_libdir}/wx/
%{_datadir}/aclocal/wxwin.m4

%changelog
%autochangelog