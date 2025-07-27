### This spec to build evolution-data-server
# - evolution-data-server (EDS): https://src.fedoraproject.org/rpms/evolution-data-server/blob/rawhide/f/evolution-data-server.spec

Name:           evolution-data-server
Version:        3.57.1
Release:        1%{?dist}
Summary:        GNOME Evolution Data Server
License:        GPL-2.0-or-later
URL:            https://gitlab.gnome.org/GNOME/evolution

Source0:        https://gitlab.gnome.org/GNOME/evolution-data-server/-/archive/%{version}/evolution-data-server-%{version}.tar.gz

BuildRequires:  cmake gcc gcc-c++ gettext pkgconfig intltool itstool
BuildRequires:  gtk4-devel gdk-pixbuf2-devel webkitgtk6.0-devel webkit2gtk4.1-devel
BuildRequires:  gnome-online-accounts-devel gnome-autoar-devel gnome-desktop3-devel
BuildRequires:  gperf gsettings-desktop-schemas-devel
BuildRequires:  nss-devel yelp-tools openldap-devel gspell-devel highlight
BuildRequires:  libsecret-devel libgweather4-devel libcanberra-devel libnotify-devel libuuid-devel
BuildRequires:  libical-devel libical-glib-devel libpst-devel libarchive-devel libnma-devel
BuildRequires:  libytnef-devel libmspack-devel

%description
This spec builds Evolution Data Server (EDS), which is a set of libraries and services

%prep
%setup -n evolution-data-server-%{version}

%build
export CFLAGS="$RPM_OPT_FLAGS -fPIC -Wno-sign-compare -Wno-deprecated-declarations"

################ Build EDS
printf "\n%s\n" "#ANCHOR: Build Evolution Data Server"
%cmake .. \
    -DCMAKE_C_FLAGS_RELEASE="${CFLAGS} -flto -march=native" \
    -DCMAKE_CXX_FLAGS_RELEASE="${CFLAGS} -flto -march=native" \
    -DCMAKE_BUILD_TYPE=Release \
    -DWITH_LIBDB=OFF -DENABLE_GTK_DOC=OFF \
    -DENABLE_OAUTH2_WEBKITGTK=ON -DENABLE_OAUTH2_WEBKITGTK4=ON \
    -DENABLE_GTK=ON
%cmake_build -j%{_smp_build_ncpus}

%install
%cmake_install

## Generate file list (include everything)
find %{buildroot} -type f | sed "s|^%{buildroot}||" > filelist.txt

%files -f filelist.txt

%changelog
%autochangelog
