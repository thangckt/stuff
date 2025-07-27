### This spec to build Evolution EWS plugin
# - evolution-ews: https://src.fedoraproject.org/rpms/evolution-ews/blob/rawhide/f/evolution-ews.spec

Name:           evolution-ews
Version:        3.57.1
Release:        1%{?dist}
Summary:        GNOME Evolution EWS plugin
License:        GPL-2.0-or-later
URL:            https://gitlab.gnome.org/GNOME/evolution

Source0:        https://gitlab.gnome.org/GNOME/evolution-ews/-/archive/%{version}/evolution-ews-%{version}.tar.gz

BuildRequires:  cmake gcc gcc-c++ pkgconfig

BuildRequires:  evolution >= %{version}
Requires:       evolution >= %{version}

%description
This spec builds Evolution EWS plugin.

%prep
%setup -n evolution-ews-%{version}

%build
export CFLAGS="$RPM_OPT_FLAGS -fPIC -Wno-sign-compare -Wno-deprecated-declarations -flto"

################ Build Evolution EWS plugin
printf "\n%s\n" "#ANCHOR: Build Evolution EWS plugin"
%cmake \
    -DINCLUDE_INSTALL_DIR:PATH=%{_includedir} \
	-DLIB_INSTALL_DIR:PATH=%{_libdir} \
	-DSYSCONF_INSTALL_DIR:PATH=%{_sysconfdir} \
	-DSHARE_INSTALL_PREFIX:PATH=%{_datadir} \
	-DLIB_SUFFIX=64
%cmake_build -j%{_smp_build_ncpus}

%install
%cmake_install

## Generate file list (include everything)
find %{buildroot} -type f | sed "s|^%{buildroot}||" > filelist.txt

%files -f filelist.txt

%changelog
%autochangelog
