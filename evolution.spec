### REF: https://www.ovito.org/docs/current/development/build_linux.html
#        https://github.com/clearlinux-pkgs/evolution/blob/main/evolution.spec

Name:           evolution
Version:        3.57.1
Release:        1%{?dist}
Summary:        Integrated email, calendar and address book for the GNOME desktop

License:        GPLv2+
URL:            https://gitlab.gnome.org/GNOME/evolution
Source0:        https://download.gnome.org/sources/evolution/%{version}/evolution-%{version}.tar.xz

BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  gcc gcc-c++
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(gsettings-desktop-schemas)
BuildRequires:  pkgconfig(gcr-4)
BuildRequires:  pkgconfig(gspell-1)
BuildRequires:  pkgconfig(libsecret-1)
BuildRequires:  pkgconfig(nspr)
BuildRequires:  pkgconfig(nss)
BuildRequires:  pkgconfig(libcanberra-gtk3)
BuildRequires:  pkgconfig(libical-glib)
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(libebackend-1.2)
BuildRequires:  pkgconfig(libedataserver-1.2)
BuildRequires:  pkgconfig(libecal-2.0)
BuildRequires:  pkgconfig(libebook-1.2)
BuildRequires:  pkgconfig(libebook-contacts-1.2)
BuildRequires:  pkgconfig(libedata-book-1.2)
BuildRequires:  pkgconfig(libedata-cal-2.0)
BuildRequires:  pkgconfig(libcamel-1.2)
BuildRequires:  pkgconfig(gweather4)
BuildRequires:  pkgconfig(libnotify)
BuildRequires:  gettext
BuildRequires:  itstool
BuildRequires:  gtk-doc
BuildRequires:  yelp-tools

%description
Evolution is the GNOME email, calendar, contact and task application. It provides integrated mail, address book and calendaring functionality to users of the GNOME desktop.

%prep
%autosetup -n evolution-%{version}

%build
%meson
%meson_build

%install
%meson_install

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