### REF: https://gitlab.gnome.org/GNOME/evolution/-/wikis/Building
#        https://github.com/clearlinux-pkgs/evolution/blob/main/evolution.spec

Name:           evolution
Version:        3.57.1
Release:        1%{?dist}
Summary:        GNOME email, calendar and contact management software with EWS plugin

License:        GPL-2.0-or-later
URL:            https://gitlab.gnome.org/GNOME/evolution
Source0:        https://gitlab.gnome.org/GNOME/evolution/-/archive/%{version}/evolution-%{version}.tar.gz
Source1:        https://gitlab.gnome.org/GNOME/evolution-ews/-/archive/%{version}/evolution-ews-%{version}.tar.gz
Source2:        https://gitlab.gnome.org/GNOME/evolution-data-server/-/archive/%{version}/evolution-data-server-%{version}.tar.gz

BuildRequires:  cmake gcc gcc-c++ gettext pkgconfig intltool
BuildRequires:  gtk4-devel gperf libuuid-devel
BuildRequires:  libsecret-devel libgweather4-devel gsettings-desktop-schemas-devel
BuildRequires:  libcanberra-devel libnotify-devel openldap-devel gspell-devel
BuildRequires:  itstool yelp-tools gdk-pixbuf2-devel libarchive-devel libnma-devel
BuildRequires:  libical-devel nss-devel webkitgtk6.0-devel
BuildRequires:  gnome-online-accounts-devel libical-glib-devel

%description
Evolution PIM application built with matching Evolution Data Server and EWS plugin support, enabling Microsoft Exchange/Outlook365 accounts.

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
    -DENABLE_OAUTH2=OFF \
    -DENABLE_OAUTH2_WEBKITGTK=OFF \
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
