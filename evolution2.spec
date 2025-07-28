### This spec to build Evolution
# - evolution: https://src.fedoraproject.org/rpms/evolution/blob/rawhide/f/evolution.spec

Name:           evolution
Version:        3.57.1
Release:        1%{?dist}
Summary:        GNOME Evolution Suite
License:        GPL-2.0-or-later
URL:            https://gitlab.gnome.org/GNOME/evolution

Source0:        https://gitlab.gnome.org/GNOME/evolution/-/archive/%{version}/evolution-%{version}.tar.gz

BuildRequires:  cmake gcc gcc-c++ pkgconfig gettext
BuildRequires:  gtk4-devel webkitgtk6.0-devel webkit2gtk4.1-devel
BuildRequires:  gnome-online-accounts-devel gnome-autoar-devel gnome-desktop3-devel gsettings-desktop-schemas-devel
BuildRequires:  nss-devel yelp-tools openldap-devel gspell-devel
BuildRequires:  libgweather4-devel libcanberra-devel libnotify-devel
BuildRequires:  gdk-pixbuf2-devel highlight intltool itstool
BuildRequires:  libpst-devel libarchive-devel libnma-devel libytnef-devel

BuildRequires:  evolution-data-server >= %{version}
Requires:       evolution-data-server >= %{version}
#Requires:      gvfs gspell highlight

%global __brp_compress true
%global __brp_mangle_shebangs true

%description
This spec builds Evolution PIM (Personal Information Manager).

%prep
%setup -n evolution-%{version}

%build
export CFLAGS="$RPM_OPT_FLAGS -fPIC -Wno-sign-compare -Wno-deprecated-declarations -flto"

################ Build Evolution
printf "\n%s\n" "#ANCHOR: Build Evolution"
%cmake \
    -DINCLUDE_INSTALL_DIR:PATH=%{_includedir} \
	-DLIB_INSTALL_DIR:PATH=%{_libdir} \
	-DSYSCONF_INSTALL_DIR:PATH=%{_sysconfdir} \
	-DSHARE_INSTALL_PREFIX:PATH=%{_datadir} \
	-DLIB_SUFFIX=64 \
    -DENABLE_PLUGINS=all \
    -DENABLE_MAINTAINER_MODE=OFF \
    -DENABLE_GTK_DOC=OFF \
    -DENABLE_MARKDOWN=OFF
%cmake_build

%install
%cmake_install

## Generate file list (include everything)
find %{buildroot} -type f | sed "s|^%{buildroot}||" > filelist.txt

%files -f filelist.txt

%changelog
%autochangelog
