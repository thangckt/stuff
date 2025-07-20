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
BuildRequires:  libical-devel nss-devel webkitgtk6.0-devel evolution-data-server-devel

%description
Evolution PIM application built with matching Evolution Data Server and EWS plugin support, enabling Microsoft Exchange/Outlook365 accounts.

%prep
%autosetup -n evolution-%{version} -a1 -a2 -S plain
ls -la

%build
# Build Evolution Data Server
cd %{_builddir}/evolution-data-server-%{version}
mkdir build-eds && cd build-eds
%cmake .. \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DCMAKE_CXX_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DWITH_LIBDB=OFF
%cmake_build

# Build Evolution
cd %{_builddir}/evolution-%{version}
mkdir build && cd build
%cmake .. \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DCMAKE_CXX_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DENABLE_GNOME_DESKTOP=OFF \
    -DWITH_LIBDB=OFF
%cmake_build

# Build Evolution-EWS
cd %{_builddir}/evolution-ews-%{version}
mkdir build-ews && cd build-ews
%cmake .. \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DCMAKE_CXX_FLAGS_RELEASE="%{optflags} -flto -march=native"
%cmake_build

%install
# Install EDS
cd %{_builddir}/evolution-data-server-%{version}
cd build-eds
%cmake_install DESTDIR=%{buildroot}

# Install Evolution
cd %{_builddir}/evolution-%{version}
cd build
%cmake_install DESTDIR=%{buildroot}

# Install Evolution-EWS
cd %{_builddir}/evolution-ews-%{version}
cd build-ews
%cmake_install DESTDIR=%{buildroot}

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