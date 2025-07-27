### This spec to build Evolution EWS plugin
# - evolution-ews: https://src.fedoraproject.org/rpms/evolution-ews/blob/rawhide/f/evolution-ews.spec

Name:           evolution-ews
Version:        3.57.1
Release:        1%{?dist}
Summary:        GNOME Evolution EWS plugin
License:        GPL-2.0-or-later
URL:            https://gitlab.gnome.org/GNOME/evolution

Source0:        https://gitlab.gnome.org/GNOME/evolution-ews/-/archive/%{version}/evolution-ews-%{version}.tar.gz

BuildRequires:  cmake gcc gcc-c++ gettext pkgconfig intltool itstool
BuildRequires:  gtk4-devel gdk-pixbuf2-devel webkitgtk6.0-devel webkit2gtk4.1-devel
BuildRequires:  gnome-online-accounts-devel gnome-autoar-devel gnome-desktop3-devel
BuildRequires:  gperf gsettings-desktop-schemas-devel
BuildRequires:  nss-devel yelp-tools openldap-devel gspell-devel highlight
BuildRequires:  libsecret-devel libgweather4-devel libcanberra-devel libnotify-devel libuuid-devel
BuildRequires:  libical-devel libical-glib-devel libpst-devel libarchive-devel libnma-devel
BuildRequires:  libytnef-devel libmspack-devel

Requires:       evolution>=3.57.1

%description
This spec builds Evolution EWS plugin.

%prep
%setup -n evolution-%{version}

%build
export CFLAGS="$RPM_OPT_FLAGS -fPIC -Wno-sign-compare -Wno-deprecated-declarations"

################ Build Evolution EWS plugin
printf "\n%s\n" "#ANCHOR: Build Evolution EWS plugin"
%cmake .. \
    -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DCMAKE_BUILD_TYPE=Release
%cmake_build -j%{_smp_build_ncpus}

%install
%cmake_install

## Generate file list (include everything)
find %{buildroot} -type f | sed "s|^%{buildroot}||" > filelist.txt

%files -f filelist.txt

%changelog
%autochangelog
