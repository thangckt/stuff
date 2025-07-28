### REF: https://gitlab.com/bgstack15/stackrpms/-/blob/master/freefilesync/freefilesync.spec?ref_type=heads

%global  pkgname FreeFileSync
%global  prog2name RealTimeSync
%global  dummy_package   0
%define  debug_package %{nil}
%define  min_libcurl %{nil}
%define  min_libssh2 %{nil}
%define  min_openssl %{nil}
%define scl_env %{nil}
%define scl_buildreq %{nil}
%if 0%{?el6}%{?el7}
   %define scl_env devtoolset-7
   %define scl_buildreq devtoolset-7-toolchain
   %define min_libcurl >= 7.61.0
   %define min_libssh2 >= 1.8.0
   %define min_openssl >= 1.1.1c
%endif
%if 0%{?el8}
   %define scl_env gcc-toolset-11
   %define scl_buildreq gcc-toolset-11-gcc-c++, gcc-toolset-11-annobin-plugin-gcc
   %define min_libcurl >= 7.61.0
   %define min_libssh2 >= 1.9.0
   %define min_openssl >= 1.1.1k
%endif
%define libssh2_name libssh2
%define openssl_name openssl
# EL8 copr has some dnf module weirdness with libssh2, not a version problem.
%if 0%{?el6}%{?el7}%{?el8}
%define libssh2_name libssh2-freefilesync
%endif
%if 0%{?el6}%{?el7}
%define openssl_name openssl-freefilesync
%endif
%if 0%{?fedora} >= 36
# https://www.spinics.net/lists/fedora-devel/msg296646.html
# https://fedoraproject.org/wiki/Changes/Package_information_on_ELF_objects
%undefine _package_note_file
%endif
Name:       freefilesync
Version:    14.3
Release:    1%{?dist}
Summary:    A file synchronization utility

Group:      Applications/File
License:    GPLv3
URL:        http://www.freefilesync.org/
# upstream does not provide easy automatic downloads of the source, so use the mirror
#Source0:    http://www.freefilesync.org/download/%%{pkgname}_%%{version}_Source.zip
Source0:    https://gitlab.com/opensource-tracking/%{pkgname}/-/archive/%{version}/%{pkgname}-%{version}.tar.gz
Source1:    %{pkgname}.desktop
Source2:    %{prog2name}.desktop
Source3:    %{name}.xml
# all rpm distros use these
Patch0:     00_allow_parallel_ops.patch
Patch1:     01_no_check_updates.patch
# fc37 has wxGTK which uses wx 3.2
#Patch2:     02_no_wx311.patch
Patch3:     03_sftp.patch
# fc37 this is more wx < 3.2 patches which are no longer necessary
#Patch4:     04_revert_zenju_aggressive_upstreamisms.patch
Patch5:     05_traditional_view.patch
Patch6:     06_icon_loader.patch
Patch7:     07_libssh2.patch
# distro specific patches
## Fedora and EL8
Patch20:    ffs_distro_fedora.patch
## EL6 and EL7
Patch30:    ffs_distro_el6_el7.patch
Patch31:    ffs_el6_el7_bit.patch
Patch32:    ffs_el6_el7_no_eraseif.patch
# dependency specific
Patch40:    ffs_openssl.patch
Patch41:    ffs_no_gcc12.patch
Patch60:    ffs_desktop_notifications.patch
Patch70:    ffs_libcurl_7.61.1.patch
Patch71:    ffs_libcurl_7.71.1.patch
Patch72:    ffs_libcurl_7.79.1.patch

Packager:   B. Stack <bgstack15@gmail.com>
BuildRequires: brotli-devel
BuildRequires: wxGTK-devel
BuildRequires: desktop-file-utils
BuildRequires: gcc-c++
BuildRequires: ImageMagick
%if "%{?min_libcurl}" != ""
BuildRequires: libcurl-devel %{min_libcurl}
%else
BuildRequires: libcurl-devel
%endif
%if "%{?min_libssh2}" != ""
BuildRequires: %{libssh2_name}-devel %{min_libssh2}
%else
BuildRequires: %{libssh2_name}-devel
%endif
BuildRequires: patch
BuildRequires: pkgconfig(giomm-2.4)
BuildRequires: pkgconfig(gtk+-3.0)
BuildRequires: pkgconfig(libselinux)
BuildRequires: pkgconfig(zlib)
# We need the binary so we can check version number
BuildRequires: %{openssl_name}
%if "%{?scl_buildreq}" != ""
BuildRequires: %{scl_buildreq}
%endif
%if "%{?min_openssl}" != ""
BuildRequires: %{openssl_name}-devel %{min_openssl}
%else
BuildRequires: %{openssl_name}-devel
%endif
#Requires: libcurl %%{?min_libcurl}
#Requires: %%{libssh2_name} %%{?min_libssh2}
#Requires: openssl-%%{name}-libs %%{?min_openssl}
Requires:      hicolor-icon-theme
Requires:      xdg-utils
Provides:      mimehandler(application/x-freefilesync-ffs)
Provides:      mimehandler(application/x-freefilesync-real)
Provides:      mimehandler(application/x-freefilesync-batch)

%description
FreeFileSync is a free Open Source software that helps you synchronize
files and synchronize folders for Windows, Linux and macOS. It is
designed to save your time setting up and running backup jobs while
having nice visual feedback along the way.

%prep
%setup -n %{pkgname}-%{version}
# fix text file line endings and permissions to unix
find . ! -type d \( -name '*.c' -o -name '*.cpp' -o -name '*.h' \) \
   -exec %{__sed} -i -r -e 's/\r$//' {} +
%patch0 -p1
%patch1 -p1
#%patch2 -p1
%patch3 -p1
#%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%if 0%{?el6}%{?el7}
# use the el patch
%patch30 -p1
%patch31 -p1
%patch32 -p1
%else
# use the fedora patch, even for el8
%patch20 -p1
%endif
# Determine if openssl < 3.0.0
opensslver="$( openssl version | awk '{if($2>=3){print "3"}else{print"1"}}' )"
if test ${opensslver} -lt 3 ;
then
%patch40 -p1
fi
# Determine if g++ < 12
g__version="$(
%if "%{?scl_env}" != ""
   scl enable %{scl_env} /bin/bash <<'EOFSCL'
%endif
   g++ --version
%if "%{?scl_env}" != ""
EOFSCL
%endif
)"
g__version="$( echo "${g__version}" | awk 'NR==1{if($3>=12){print "12"}else{print"11"}}' )"
echo "G__version=${g_version}"
if test ${g__version} -lt 12 ;
then
%patch41 -p1
fi
# desktop notifications merely has to happen after distro patch
%patch60 -p1
# Determine version of libcurl
%define libcurl_ver %( rpm -q libcurl-devel --queryformat '%%{version}' )
case "%{libcurl_ver}" in
   7.61.1)
%patch70 -p1
      ;;
   7.79.1)
%patch72 -p1
      ;;
   7.85.0 | 7.87.0 | 7.88.1 )
      # fc37 | fc38 | rawhide
      echo "no patch necessary for libcurl %{libcurl_ver}"
      ;;
   *)
%patch71 -p1
      ;;
esac

# custom build parameters for packaging application in rpm
# fedora provides build_cxxflags, which is really just optflags
%{__sed} \
  -e 's|-O3 -DNDEBUG|-DNDEBUG -D"warn_static(arg)= " -DZEN_LINUX %{?build_cxxflags:%{build_cxxflags}}%{!?build_cxxflags:%{optflags}}|g' \
  -e '/linkFlags/s|-s|%{__global_ldflags}|;' \
  -i %{pkgname}/Source/Makefile %{pkgname}/Source/%{prog2name}/Makefile

%build
export TMPDIR=/tmp # necessary since 11.0
%if !%{dummy_package}
   %if "%{?scl_env}" != ""
      scl enable %{scl_env} /bin/bash << 'EOFSCL'
   %endif
   %make_build -C %{pkgname}/Source
   %make_build -C %{pkgname}/Source/%{prog2name}
   %if "%{?scl_env}" != ""
EOFSCL
   %endif
%endif

%install
%if !%{dummy_package}
# removed by upstream around version 11
#%%make_install -C %%{pkgname}/Source
#%%make_install -C %%{pkgname}/Source/%%{prog2name}
pushd %{pkgname}/Build
install -d %{buildroot}%{_bindir} %{buildroot}%{_datadir}/%{name}
install -Dm 0755 -t %{buildroot}%{_bindir} Bin/%{pkgname} Bin/%{prog2name}
cd Resources ; cp -pr * %{buildroot}%{_datadir}/%{name}
popd
%endif

# make extra sure the files are not marked with executable
find %{buildroot}%{_datadir}/%{name} -type f -exec chmod -x '{}' \; || :

# desktop files
mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install --dir %{buildroot}%{_datadir}/applications %{SOURCE1}
desktop-file-install --dir %{buildroot}%{_datadir}/applications %{SOURCE2}

# mimetypes
install -d %{buildroot}%{_datadir}/mime/packages
install -Dm 0644 -t %{buildroot}%{_datadir}/mime/packages %{SOURCE3}

# icons
unzip %{pkgname}/Build/Resources/Icons.zip cfg_batch.png start_sync.png %{pkgname}.png %{prog2name}.png

ff=" -filter Lanczos"
for res in 16 22 24 32 48 64 96 128 256 ;do
  dir=%{buildroot}%{_datadir}/icons/hicolor/${res}x${res}
  rr=" -resize ${res}x${res}"
  mkdir -p ${dir}/apps ${dir}/mimetypes
  # apps
  convert %{pkgname}.png ${ff} ${rr} ${dir}/apps/%{pkgname}.png
  convert %{prog2name}.png ${ff} ${rr} ${dir}/apps/%{prog2name}.png
  # mimetypes
  convert cfg_batch.png ${ff} ${rr} ${dir}/mimetypes/application-x-freefilesync-batch.png
  convert start_sync.png ${ff} ${rr} ${dir}/mimetypes/application-x-freefilesync-ffs.png
  convert %{prog2name}.png ${ff} ${rr} ${dir}/mimetypes/application-x-freefilesync-real.png
done

%clean
%{__rm} -rf %{buildroot} || :

%post
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
if test "$1" = "0" ;
then
   touch --no-create %{_datadir}/icons/hicolor &>/dev/null
fi

%posttrans
update-desktop-database 1>/dev/null 2>&1 & :
gtk-update-icon-cache %{_datadir}/icons/hicolor 1>/dev/null 2>&1 & :
update-mime-database -n ${_datadir}/mime 1>/dev/null 2>&1 & :

%files
%license %attr(444, -, -) License.txt
%doc %attr(444, -, -) Changelog.txt
%{_bindir}/%{pkgname}
%{_bindir}/%{prog2name}
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*x*/*/*.png
%{_datadir}/mime/packages/*
%{_datadir}/%{name}
%ghost %config %attr(666, -, -) %{_datadir}/%{name}/GlobalSettings.xml

%changelog
%autochangelog