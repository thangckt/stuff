### This spec to build Evolution with EWS support. This unify 3 speparated builds:
# - evolution-data-server (EDS): https://src.fedoraproject.org/rpms/evolution-data-server/blob/rawhide/f/evolution-data-server.spec
# - evolution: https://src.fedoraproject.org/rpms/evolution/blob/rawhide/f/evolution.spec
# - evolution-ews: https://src.fedoraproject.org/rpms/evolution-ews/blob/rawhide/f/evolution-ews.spec


Name:           evolution-ews
Version:        3.57.1
Release:        1%{?dist}
Summary:        GNOME PIM (Evolution + EDS + EWS plugin unified build)
License:        GPL-2.0-or-later
URL:            https://gitlab.gnome.org/GNOME/evolution

Source0:        https://gitlab.gnome.org/GNOME/evolution-ews/-/archive/%{version}/evolution-ews-%{version}.tar.gz
Source1:        https://gitlab.gnome.org/GNOME/evolution/-/archive/%{version}/evolution-%{version}.tar.gz
Source2:        https://gitlab.gnome.org/GNOME/evolution-data-server/-/archive/%{version}/evolution-data-server-%{version}.tar.gz

BuildRequires:  cmake gcc gcc-c++ gettext pkgconfig intltool
BuildRequires:  gtk4-devel gperf libuuid-devel
BuildRequires:  libsecret-devel libgweather4-devel gsettings-desktop-schemas-devel
BuildRequires:  libcanberra-devel libnotify-devel openldap-devel gspell-devel
BuildRequires:  itstool yelp-tools gdk-pixbuf2-devel libarchive-devel libnma-devel
BuildRequires:  libical-devel nss-devel webkitgtk6.0-devel
BuildRequires:  gnome-online-accounts-devel libical-glib-devel webkit2gtk4.1-devel

%description
This spec builds Evolution PIM as a unified package including matching versions of Evolution, Evolution Data Server (EDS),
and the EWS plugin. Supports Microsoft Exchange/Outlook365 accounts via the EWS plugin.

%prep
%setup -q -n evolution-ews-%{version}
tar -xf %{SOURCE1}
tar -xf %{SOURCE2}
# The topdir must the same as package name (from source0), other sources will be unpacked into the topdir

# ls -1  # for debugging, check if sources are unpacked correctly

%build
export LOCALPREFIX=%{_builddir}/evolution-ews-%{version}/localprefix
export PKG_CONFIG_PATH="$LOCALPREFIX/lib64/pkgconfig:$LOCALPREFIX/lib/pkgconfig:$PKG_CONFIG_PATH"
export LD_LIBRARY_PATH="$LOCALPREFIX/lib64:$LOCALPREFIX/lib:$LD_LIBRARY_PATH"
export CFLAGS="$RPM_OPT_FLAGS -fPIC -Wno-sign-compare -Wno-deprecated-declarations"

# Build EDS
cd evolution-data-server-%{version}
mkdir build-eds && cd build-eds
%cmake .. \
    -DCMAKE_INSTALL_PREFIX=$LOCALPREFIX \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DCMAKE_CXX_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DWITH_LIBDB=OFF -DENABLE_GTK_DOC=OFF \
    -DENABLE_OAUTH2_WEBKITGTK=ON -DENABLE_OAUTH2_WEBKITGTK4=ON \
    -DENABLE_GTK=ON
%cmake_build
cmake --install . --prefix $LOCALPREFIX
cd ../..

# (Debug) See if some libs are built and install correctly
find $LOCALPREFIX -name "camel-1.2.pc"

# Build Evolution
cd evolution-%{version}
mkdir build && cd build
%cmake .. \
    -DCMAKE_PREFIX_PATH="$LOCALPREFIX:$LOCALPREFIX/lib64/cmake:$LOCALPREFIX/lib/cmake" \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_BUILD_TYPE=Release -DENABLE_PLUGINS=all \
    -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DCMAKE_CXX_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DWITH_LIBDB=OFF -DENABLE_GTK_DOC=OFF \
    -DENABLE_GNOME_DESKTOP=OFF
%cmake_build
cd ../..

# Build EWS plugin
mkdir build && cd build
%cmake .. \
    -DCMAKE_PREFIX_PATH="$LOCALPREFIX:$LOCALPREFIX/lib64/cmake:$LOCALPREFIX/lib/cmake" \
    -DCMAKE_PREFIX_PATH=$LOCALPREFIX \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DCMAKE_CXX_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DENABLE_GTK_DOC=OFF
%cmake_build

%install
# Copy locally installed EDS into buildroot
mkdir -p %{buildroot}%{_prefix}
cp -a $LOCALPREFIX/* %{buildroot}%{_prefix}/

# Install Evolution
pushd evolution-%{version}/build
%cmake_install
popd

# Install EWS
pushd build
%cmake_install
popd

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

%{_libdir}/evolution/plugins/liborg-gnome-exchange-ews.so
%{_datadir}/evolution/ui/org-gnome-exchange-ews.ui

%{_libdir}/evolution-data-server-*/  # EDS libraries and modules installed
%{_mandir}/man1/evolution.1.gz

%changelog
%autochangelog
