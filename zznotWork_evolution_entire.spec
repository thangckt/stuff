### This spec to build Evolution with EWS support. This unify 3 speparated builds:
# - evolution-data-server (EDS): https://src.fedoraproject.org/rpms/evolution-data-server/blob/rawhide/f/evolution-data-server.spec
# - evolution: https://src.fedoraproject.org/rpms/evolution/blob/rawhide/f/evolution.spec
# - evolution-ews: https://src.fedoraproject.org/rpms/evolution-ews/blob/rawhide/f/evolution-ews.spec

### Note: this approach does not work, due to paths issues.

Name:           evolution
Version:        3.57.1
Release:        1%{?dist}
Summary:        GNOME PIM (Evolution + EDS + EWS plugin unified build)
License:        GPL-2.0-or-later
URL:            https://gitlab.gnome.org/GNOME/evolution

Source0:        https://gitlab.gnome.org/GNOME/evolution/-/archive/%{version}/evolution-%{version}.tar.gz
Source1:        https://gitlab.gnome.org/GNOME/evolution-ews/-/archive/%{version}/evolution-ews-%{version}.tar.gz
Source2:        https://gitlab.gnome.org/GNOME/evolution-data-server/-/archive/%{version}/evolution-data-server-%{version}.tar.gz

BuildRequires:  cmake gcc gcc-c++ gettext pkgconfig intltool itstool
BuildRequires:  gtk4-devel gdk-pixbuf2-devel webkitgtk6.0-devel webkit2gtk4.1-devel
BuildRequires:  gnome-online-accounts-devel gnome-autoar-devel gnome-desktop3-devel
BuildRequires:  gperf gsettings-desktop-schemas-devel
BuildRequires:  nss-devel yelp-tools openldap-devel gspell-devel highlight
BuildRequires:  libsecret-devel libgweather4-devel libcanberra-devel libnotify-devel libuuid-devel
BuildRequires:  libical-devel libical-glib-devel libpst-devel libarchive-devel libnma-devel
BuildRequires:  libytnef-devel libmspack-devel chrpath

%global _local_prefix %{_builddir}/localprefix
%global __brp_compress true
%global __brp_mangle_shebangs true
%define _libdir /usr/lib64

%description
This spec builds Evolution PIM as a unified package including matching versions of Evolution, Evolution Data Server (EDS),
and the EWS plugin. Supports Microsoft Exchange/Outlook365 accounts via the EWS plugin.

%prep
%setup -q -n evolution-%{version}
tar -xf %{SOURCE1}
tar -xf %{SOURCE2}
# The topdir must the same as package name (from source0), other sources will be unpacked into the topdir

# ls -1  # for debugging, check if sources are unpacked correctly

%build
export CFLAGS="$RPM_OPT_FLAGS -fPIC -Wno-sign-compare -Wno-deprecated-declarations"

################ Step 1: Build and install EDS
printf "\n%s\n" "#ANCHOR: Build Evolution Data Server"
cd evolution-data-server-%{version}
rm -rf build_eds && mkdir build_eds
cd build_eds
cmake .. \
    -DCMAKE_C_FLAGS_RELEASE="${CFLAGS} -flto -march=native" \
    -DCMAKE_CXX_FLAGS_RELEASE="${CFLAGS} -flto -march=native" \
    -DCMAKE_INSTALL_PREFIX=%{_local_prefix} \
    -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
    -DCMAKE_BUILD_TYPE=Release \
    -DWITH_LIBDB=OFF -DENABLE_GTK_DOC=OFF \
    -DENABLE_OAUTH2_WEBKITGTK=ON -DENABLE_OAUTH2_WEBKITGTK4=ON \
    -DENABLE_GTK=ON
cmake --build . -j%{_smp_build_ncpus}
cmake --install .
cd ../..

##(Debug) See if some libs are built and install correctly
find %{_local_prefix} -name "camel-1.2.pc"

################ Step 2: Build and install Evolution
export PKG_CONFIG_PATH="%{_local_prefix}/lib64/pkgconfig:%{_local_prefix}/lib/pkgconfig:$PKG_CONFIG_PATH"
export LD_LIBRARY_PATH="%{_local_prefix}/lib64:%{_local_prefix}/lib:$LD_LIBRARY_PATH"
export CMAKE_PREFIX_PATH="%{_local_prefix}:$CMAKE_PREFIX_PATH"
export PATH="%{_local_prefix}/bin:$PATH"
export XDG_DATA_DIRS="%{_local_prefix}/share:$XDG_DATA_DIRS"

printf "\n%s\n" "#ANCHOR: Build Evolution"
rm -rf build_ev && mkdir build_ev
cd build_ev
cmake .. \
    -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DCMAKE_INSTALL_PREFIX=%{_local_prefix} \
    -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
    -DCMAKE_BUILD_TYPE=Release \
    -DENABLE_PLUGINS=all \
    -DENABLE_MAINTAINER_MODE=OFF \
    -DENABLE_GTK_DOC=OFF \
    -DENABLE_MARKDOWN=OFF
cmake --build . -j%{_smp_build_ncpus}
cmake --install .
cd ..

################ Step 3: Build EWS plugin against EDS and Evolution
printf "\n%s\n" "#ANCHOR: Build Evolution EWS plugin"
cd evolution-ews-%{version}
rm -rf build_ews && mkdir build_ews
cd build_ews
cmake .. \
    -DCMAKE_C_FLAGS_RELEASE="%{optflags} -flto -march=native" \
    -DCMAKE_INSTALL_PREFIX=%{_local_prefix} \
    -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
    -DCMAKE_BUILD_TYPE=Release
cmake --build . -j%{_smp_build_ncpus}
cmake --install .
cd ../..

%install
export QA_RPATHS=$[ 0x002|0x008 ]

mkdir -p %{buildroot}%{_prefix}
cp -a %{_local_prefix}/* %{buildroot}%{_prefix}/

# Fix RPATHs for ELF binaries under /usr/lib/evolution
find %{buildroot}/usr/lib/evolution -type f | while read f; do
  file "$f" | grep -q ELF && chrpath -r %{_libdir}/evolution "$f" || :
done

# ✅ Move .so files manually from /usr/lib to /usr/lib64
mkdir -p %{buildroot}%{_libdir}
if [ -d %{buildroot}/usr/lib ]; then
  find %{buildroot}/usr/lib -maxdepth 1 -name "*.so*" -exec mv -v {} %{buildroot}%{_libdir}/ \;
  rmdir --ignore-fail-on-non-empty %{buildroot}/usr/lib
fi

## Debug
find %{buildroot} -name "libevolution-shell.so*"

## Generate file list (include everything)
find %{buildroot} -type f | sed "s|^%{buildroot}||" > filelist.txt

%files -f filelist.txt
/usr/lib/lib*.so*

%changelog
%autochangelog
