### This spec to build evolution-data-server
# - evolution-data-server (EDS): https://src.fedoraproject.org/rpms/evolution-data-server/blob/rawhide/f/evolution-data-server.spec

Name:           evolution-data-server
Version:        3.57.1
Release:        1%{?dist}
Summary:        GNOME Evolution Data Server
License:        GPL-2.0-or-later
URL:            https://gitlab.gnome.org/GNOME/evolution

Source0:        https://gitlab.gnome.org/GNOME/evolution-data-server/-/archive/%{version}/evolution-data-server-%{version}.tar.gz

BuildRequires:  cmake gcc gcc-c++ pkgconfig gettext gperf vala
BuildRequires:  gtk4-devel webkitgtk6.0-devel webkit2gtk4.1-devel
BuildRequires:  gnome-online-accounts-devel gnome-autoar-devel gnome-desktop3-devel gsettings-desktop-schemas-devel
BuildRequires:  nss-devel yelp-tools openldap-devel gspell-devel
BuildRequires:  libsecret-devel libgweather4-devel libcanberra-devel libnotify-devel libuuid-devel libical-devel libical-glib-devel

%description
This spec builds Evolution Data Server (EDS), which is a set of libraries and services

%prep
%setup -n evolution-data-server-%{version}

%build
export CFLAGS="$RPM_OPT_FLAGS -fPIC -Wno-sign-compare -Wno-deprecated-declarations -flto"
export CPPFLAGS="-I%{_includedir}/et -flto"

################ Build EDS
printf "\n%s\n" "#ANCHOR: Build Evolution Data Server"
%cmake \
    -DWITH_SYSTEMDUSERUNITDIR=%{_userunitdir} \
	-DINCLUDE_INSTALL_DIR:PATH=%{_includedir} \
	-DLIB_INSTALL_DIR:PATH=%{_libdir} \
	-DSYSCONF_INSTALL_DIR:PATH=%{_sysconfdir} \
	-DSHARE_INSTALL_PREFIX:PATH=%{_datadir} \
	-DLIB_SUFFIX=64 \
    -DWITH_LIBDB=OFF -DENABLE_GTK_DOC=OFF \
    -DENABLE_OAUTH2_WEBKITGTK=ON -DENABLE_OAUTH2_WEBKITGTK4=ON \
    -DENABLE_GTK=ON
%cmake_build -j%{_smp_build_ncpus}

%install
%cmake_install

## Generate file list (include everything)
find %{buildroot} -type f | sed "s|^%{buildroot}||" > filelist.txt

%files -f filelist.txt
%{_libdir}/libcamel-1.2.so
%{_libdir}/libebackend-1.2.so
%{_libdir}/libebook-1.2.so
%{_libdir}/libebook-contacts-1.2.so
%{_libdir}/libecal-2.0.so
%{_libdir}/libedata-book-1.2.so
%{_libdir}/libedata-cal-2.0.so
%{_libdir}/libedataserver-1.2.so
%{_libdir}/libedataserverui-1.2.so
%{_libdir}/libedataserverui4-1.0.so
%{_libdir}/libcamel-1.2.so.65
%{_libdir}/libebackend-1.2.so.11
%{_libdir}/libebook-1.2.so.21
%{_libdir}/libebook-contacts-1.2.so.4
%{_libdir}/libecal-2.0.so.3
%{_libdir}/libedata-book-1.2.so.27
%{_libdir}/libedata-cal-2.0.so.2
%{_libdir}/libedataserver-1.2.so.27
%{_libdir}/libedataserverui-1.2.so.4
%{_libdir}/libedataserverui4-1.0.so.0

%changelog
%autochangelog
