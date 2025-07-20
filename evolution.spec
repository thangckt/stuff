### REF: https://github.com/GNOME/evolution/blob/master/.gitlab-ci.yml
#        https://github.com/clearlinux-pkgs/evolution/blob/main/evolution.spec

Name:           evolution
Version:        3.57.1
Release:        1%{?dist}
Summary:        Integrated email, calendar and address book for the GNOME desktop

License:        GPLv2+
URL:            https://gitlab.gnome.org/GNOME/evolution
Source0:        %{url}/-/archive/%{version}/evolution-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  gettext
BuildRequires:  gtk3-devel
BuildRequires:  evolution-data-server-devel
BuildRequires:  libnotify-devel
BuildRequires:  libcanberra-devel
BuildRequires:  libsecret-devel
BuildRequires:  libgweather4-devel
BuildRequires:  webkit2gtk3-devel
BuildRequires:  gsettings-desktop-schemas-devel
BuildRequires:  yelp-tools
BuildRequires:  intltool
BuildRequires:  gperf
BuildRequires:  itstool
BuildRequires:  nss-devel
BuildRequires:  libical-devel
BuildRequires:  gcr4-devel
BuildRequires:  libhandy1-devel
BuildRequires:  openldap-devel
BuildRequires:  gdk-pixbuf2-devel
BuildRequires:  libarchive-devel
BuildRequires:  libnma-devel
BuildRequires:  libxml2-devel
BuildRequires:  zlib-devel
BuildRequires:  glib2-devel
BuildRequires:  pango-devel

%description
Evolution is the GNOME email, calendar, contact and task application. It provides integrated mail, address book and calendaring functionality to users of the GNOME desktop.

%prep
%autosetup -n evolution-%{version}

%build
mkdir build
cd build
%cmake .. \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DCMAKE_CXX_FLAGS_RELEASE="%{optflags} -flto -march=native"
%cmake_build

%install
%make_install

%files
%license COPYING
%doc NEWS README.md
%{_bindir}/evolution
%{_datadir}/applications/org.gnome.Evolution.desktop
%{_datadir}/icons/hicolor/*/apps/org.gnome.Evolution*.svg
%{_datadir}/glib-2.0/schemas/org.gnome.evolution*.gschema.xml
%{_libexecdir}/evolution*
%{_datadir}/evolution
%{_libdir}/evolution
%{_mandir}/man1/evolution.1.gz

%changelog
%autochangelog