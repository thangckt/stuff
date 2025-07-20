### REF: https://gitlab.gnome.org/GNOME/evolution/-/wikis/Building
#        https://github.com/clearlinux-pkgs/evolution/blob/main/evolution.spec

Name:           evolution
Version:        3.57.1
Release:        1%{?dist}
Summary:        GNOME email, calendar and contact management software with EWS plugin

License:        GPL-2.0-or-later
URL:            https://gitlab.gnome.org/GNOME/evolution
Source0:        %{url}/-/archive/%{version}/evolution-%{version}.tar.gz
Source1:        %{url}/-/archive/%{version}/evolution-ews-%{version}.tar.gz

BuildRequires:  cmake gcc gcc-c++ meson gettext
BuildRequires:  gtk4-devel evolution-data-server-devel >= 3.47
BuildRequires:  webkit2gtk-5.0-devel libsecret-devel libgweather4-devel
BuildRequires:  gsettings-desktop-schemas-devel libcanberra-devel libnotify-devel
BuildRequires:  openldap-devel gcr4-devel gspell-devel itstool yelp-tools
BuildRequires:  gdk-pixbuf2-devel libarchive-devel libnma-devel libical-devel
BuildRequires:  nss-devel pkgconfig

BuildRequires:  libcurl-devel krb5-devel libsoup3-devel

%description
Evolution is a personal information management application that provides integrated mail, calendaring and address book functionality. This package also includes the Evolution-EWS plugin for Microsoft Exchange and Outlook 365 support.

%prep
%autosetup -n evolution-%{version} -a1

# Source1 (evolution-ews) is extracted into subdir: evolution-ews-%{version}
# We'll build it separately after Evolution

%build
mkdir build
cd build
%cmake .. \
  -DCMAKE_INSTALL_PREFIX=%{_prefix} \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
  -DCMAKE_CXX_FLAGS_RELEASE="%{optflags} -flto -march=native"
%cmake_build
cd ..

# Now build evolution-ews
mkdir build-ews
cd build-ews
%cmake ../evolution-ews-%{version} \
  -DCMAKE_INSTALL_PREFIX=%{_prefix} \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
  -DCMAKE_CXX_FLAGS_RELEASE="%{optflags} -flto -march=native"
%cmake_build
cd ..

%install
cd build
%cmake_install
cd ..

cd build-ews
%cmake_install
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

# Man page
%{_mandir}/man1/evolution.1.gz

%changelog
%autochangelog