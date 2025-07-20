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
BuildRequires:  gtk4-devel evolution-data-server-devel >= 3.47
BuildRequires:  libsecret-devel libgweather4-devel gsettings-desktop-schemas-devel
BuildRequires:  libcanberra-devel libnotify-devel openldap-devel gspell-devel
BuildRequires:  itstool yelp-tools gdk-pixbuf2-devel libarchive-devel libnma-devel
BuildRequires:  libical-devel nss-devel webkitgtk6.0-devel evolution-data-server-devel

%description
Evolution PIM application built with matching Evolution Data Server and EWS plugin support, enabling Microsoft Exchange/Outlook365 accounts.

%prep
%autosetup -n evolution-%{version}
%autosetup -a1 -n evolution-ews-%{version}
%autosetup -a2 -n evolution-data-server-%{version}

%build
# Build Evolution Data Server
mkdir build-eds && cd build-eds
%cmake ../evolution-data-server-%{version} \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DCMAKE_CXX_FLAGS_RELEASE="%{optflags} -flto -march=native"
%cmake_build
cd ..

# Build Evolution
mkdir build && cd build
%cmake ../evolution-%{version} \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DCMAKE_CXX_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DENABLE_GNOME_DESKTOP=OFF
%cmake_build
cd ..

# Build Evolution-EWS
mkdir build-ews && cd build-ews
%cmake ../evolution-ews-%{version} \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DCMAKE_CXX_FLAGS_RELEASE="%{optflags} -flto -march=native"
%cmake_build
cd ..

%install
# Install EDS
cd build-eds
%cmake_install DESTDIR=%{buildroot}
cd ..

# Install Evolution
cd build
%cmake_install DESTDIR=%{buildroot}
cd ..

# Install Evolution-EWS
cd build-ews
%cmake_install DESTDIR=%{buildroot}
cd ..

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