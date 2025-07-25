### REF: https://src.fedoraproject.org/rpms/evolution-data-server/blob/rawhide/f/evolution-data-server.spec

### Abstract ###
Name: evolution-data-server
Version: 3.57.1
Release: 2%{?dist}
Summary: Backend data server for Evolution
License: LGPL-2.0-or-later
URL: https://gitlab.gnome.org/GNOME/evolution/-/wikis/home
Source: http://download.gnome.org/sources/%{name}/3.57/%{name}-%{version}.tar.xz

### Dependencies ###

Requires: %{name}-langpacks = %{version}-%{release}

### Build Dependencies ###

BuildRequires: cmake
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: gettext
BuildRequires: gperf
%if %{with_docs}
BuildRequires: gtk-doc >= %{gtk_doc_version}
%endif
BuildRequires: vala
BuildRequires: systemd

BuildRequires: pkgconfig(gio-2.0) >= %{glib2_version}
BuildRequires: pkgconfig(gio-unix-2.0) >= %{glib2_version}
BuildRequires: pkgconfig(gmodule-2.0) >= %{glib2_version}
BuildRequires: pkgconfig(icu-i18n)
BuildRequires: pkgconfig(gtk+-3.0) >= %{gtk3_version}
BuildRequires: pkgconfig(gtk4) >= %{gtk4_version}
BuildRequires: pkgconfig(goa-1.0) >= %{goa_version}
BuildRequires: pkgconfig(gweather4) >= %{libgweather_version}
BuildRequires: pkgconfig(libical-glib) >= %{libical_version}
BuildRequires: pkgconfig(libsecret-unstable) >= %{libsecret_version}
BuildRequires: pkgconfig(libsoup-3.0) >= %{libsoup_version}
BuildRequires: pkgconfig(libxml-2.0)
BuildRequires: pkgconfig(nspr)
BuildRequires: pkgconfig(nss) >= %{nss_version}
BuildRequires: pkgconfig(sqlite3) >= %{sqlite_version}
BuildRequires: pkgconfig(uuid) >= %{uuid_version}
%if %{with_webkitgtk}
BuildRequires: pkgconfig(webkit2gtk-4.1) >= %{webkit2gtk_version}
BuildRequires: pkgconfig(webkitgtk-6.0) >= %{webkit2gtk4_version}
%endif
BuildRequires: pkgconfig(json-glib-1.0) >= %{json_glib_version}
BuildRequires: pkgconfig(libcanberra-gtk3)

%if %{ldap_support}
BuildRequires: openldap-devel >= 2.0.11
%if %{static_ldap}
BuildRequires: pkgconfig(openssl)
%endif
%endif

%if %{krb5_support}
BuildRequires: krb5-devel >= 1.11
%endif

%if %{phonenum_support}
BuildRequires: libphonenumber-devel
BuildRequires: protobuf-devel
BuildRequires: boost-devel
BuildRequires: abseil-cpp-devel
%endif

# libical 3.0.16 added new API, this ensures to bring it in
Requires: libical-glib >= %{libical_version}

%description
The %{name} package provides a unified backend for programs that work
with contacts, tasks, and calendar information.

It was originally developed for Evolution (hence the name), but is now used
by other packages.

%prep
# Unpack main tarball
%setup -q -n evolution-%{version}

# Unpack the extra sources manually
tar -xf %{SOURCE1}
tar -xf %{SOURCE2}
ls -la

%build
# Set up local install prefix and PKG_CONFIG/LIBRARY path overrides
export LOCALPREFIX=%{_builddir}/localprefix
export PKG_CONFIG_PATH="$LOCALPREFIX/lib64/pkgconfig:$LOCALPREFIX/lib/pkgconfig:$PKG_CONFIG_PATH"
export LD_LIBRARY_PATH="$LOCALPREFIX/lib64:$LOCALPREFIX/lib:$LD_LIBRARY_PATH"

# Build and install evolution-data-server (EDS)
cd %{_builddir}/evolution-%{version}/evolution-data-server-%{version}
mkdir build-eds && cd build-eds
%cmake .. \
    -DCMAKE_INSTALL_PREFIX=$LOCALPREFIX \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DCMAKE_CXX_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DWITH_LIBDB=OFF \
    -DENABLE_GTK_DOC=OFF \
    -DENABLE_OAUTH2=OFF \
    -DENABLE_OAUTH2_WEBKITGTK=OFF \
    -DENABLE_GTK=ON
%cmake_build
%cmake_install

# Build Evolution using the locally installed EDS
cd %{_builddir}/evolution-%{version}
mkdir build && cd build
%cmake .. \
    -DCMAKE_PREFIX_PATH=$LOCALPREFIX \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DCMAKE_CXX_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DWITH_LIBDB=OFF \
    -DENABLE_GTK_DOC=OFF \
    -DENABLE_GNOME_DESKTOP=OFF
%cmake_build

# Build evolution-ews using the local EDS install
cd %{_builddir}/evolution-%{version}/evolution-ews-%{version}
mkdir build && cd build
%cmake .. \
    -DCMAKE_PREFIX_PATH=$LOCALPREFIX \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DCMAKE_CXX_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DENABLE_GTK_DOC=OFF
%cmake_build


%install
# Install EDS to system root from localprefix
cp -a $LOCALPREFIX/* %{buildroot}/%{_prefix}

# Install Evolution
cd %{_builddir}/evolution-%{version}/build
%cmake_install

# Install Evolution-EWS
cd %{_builddir}/evolution-%{version}/evolution-ews-%{version}/build
%cmake_install

%files
%license COPYING
%doc NEWS README.md

%{_bindir}/evolution
%{_libexecdir}/evolution*
%{_libdir}/evolution
%{_datadir}/evolution
%{_datadir}/applications/org.gnome.Evolution.desktop
%{_datadir}/metainfo/org.gnome.Evolution.appdata.xml
%{_datadir}/icons/hicolor/*/apps/org.gnome.Evolution*.svg
%{_datadir}/glib-2.0/schemas/org.gnome.evolution*.gschema.xml

# EWS plugin
%{_libdir}/evolution/plugins/liborg-gnome-exchange-ews.so
%{_datadir}/evolution/ui/org-gnome-exchange-ews.ui

# EDS components
%{_libdir}/evolution-data-server-*/  # Adjust per actual install path

%{_mandir}/man1/evolution.1.gz

%changelog
%autochangelog
