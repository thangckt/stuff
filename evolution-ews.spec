Name:           evolution-ews
Version:        3.57.1
Release:        1%{?dist}
Summary:        Evolution plugin to connect to Microsoft Exchange servers via EWS

License:        GPLv2+
URL:            https://gitlab.gnome.org/GNOME/evolution-ews
Source0:        %{url}/-/archive/%{version}/evolution-ews-%{version}.tar.gz

BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  gcc gcc-c++
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(gobject-introspection-1.0)
BuildRequires:  pkgconfig(libedataserver-1.2)
BuildRequires:  pkgconfig(libecal-2.0)
BuildRequires:  pkgconfig(libical-glib)
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  evolution-data-server-devel
BuildRequires:  evolution-devel

Requires:       evolution%{?_isa} = %{version}-%{release}

%description
This package allows Evolution to connect to Microsoft Exchange servers using the Exchange Web Services (EWS) protocol, including Outlook365.

%prep
%autosetup -n evolution-ews-%{version}

%build
%meson
%meson_build

%install
%meson_install

%files
%license COPYING
%doc README.md NEWS
%{_libdir}/evolution/modules/module-ews.so
%{_datadir}/glib-2.0/schemas/org.gnome.Evolution.Ews.gschema.xml
%{_datadir}/evolution/ews/
%{_libexecdir}/evolution-ews-autoconfig

%changelog
%autochangelog