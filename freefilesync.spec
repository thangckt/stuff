### REF: https://gitlab.com/bgstack15/stackrpms/-/blob/master/freefilesync/freefilesync.spec?ref_type=heads

### Macros Section
%global pkgname FreeFileSync
%global prog2name RealTimeSync


Name:       freefilesync
Version:    14.4
Release:    1%{?dist}
Summary:    A file synchronization utility
License:    GPLv3
URL:        http://www.freefilesync.org/

# upstream does not provide easy automatic downloads of the source, so use the mirror
#Source0:    http://www.freefilesync.org/download/%%{pkgname}_%%{version}_Source.zip
Source0:    https://gitlab.com/opensource-tracking/%{pkgname}/-/archive/%{version}/%{pkgname}-%{version}.tar.gz
Source1:    %{pkgname}.desktop
Source2:    %{prog2name}.desktop
Source3:    %{name}.xml

# these patches support only some new distros
Patch0:  00_allow_parallel_ops.patch
Patch1:  01_no_check_updates.patch
Patch3:  03_sftp.patch
Patch5:  05_traditional_view.patch
Patch6:  06_icon_loader.patch
Patch7:  07_libssh2.patch
Patch20: ffs_distro_fedora.patch
Patch40: ffs_openssl.patch
Patch41: ffs_no_gcc12.patch
Patch60: ffs_desktop_notifications.patch
Patch71: ffs_libcurl_7.71.1.patch
Patch72: ffs_libcurl_7.79.1.patch

BuildRequires:  gcc-c++ brotli-devel wxGTK-devel ImageMagick unzip
BuildRequires:  desktop-file-utils patch
BuildRequires:  pkgconfig(giomm-2.4) pkgconfig(gtk+-3.0) pkgconfig(libselinux) pkgconfig(zlib)
BuildRequires:  libcurl-devel libssh2-devel openssl openssl-devel

Requires:       hicolor-icon-theme xdg-utils
Provides:       mimehandler(application/x-freefilesync-ffs)
Provides:       mimehandler(application/x-freefilesync-real)
Provides:       mimehandler(application/x-freefilesync-batch)

%description
FreeFileSync is an open-source software that helps synchronize files and folders on Windows, Linux, and macOS.
It is optimized for backup speed and visual usability.

%prep
%setup -n %{pkgname}-%{version}

# Convert CRLF to LF
find . ! -type d \( -name '*.c' -o -name '*.cpp' -o -name '*.h' \) -exec sed -i 's/\r$//' {} +

# Apply base patches
%autopatch -p1

# Fedora/RHEL 9+ base patch
%patch -P 20 -p1

# Desktop notifications
%patch -P 60 -p1

# Apply OpenSSL patch if version < 3
opensslver=$(openssl version | awk '{print $2}' | cut -d. -f1)
if [ "$opensslver" -lt 3 ]; then
    echo "Applying patch 40 for OpenSSL < 3"
    patch -p1 < %{_sourcedir}/ffs_openssl.patch
fi

# Apply GCC patch if version < 12
gccver=$(g++ -dumpversion | cut -d. -f1)
if [ "$gccver" -lt 12 ]; then
    echo "Applying patch 41 for GCC < 12"
    patch -p1 < %{_sourcedir}/ffs_no_gcc12.patch
fi

# Apply libcurl patch depending on version
libcurl_ver=$(rpm -q libcurl-devel --queryformat '%{version}')
case "$libcurl_ver" in
    7.71.1) patch -p1 < %{_sourcedir}/ffs_libcurl_7.71.1.patch ;;
    7.79.1) patch -p1 < %{_sourcedir}/ffs_libcurl_7.79.1.patch ;;
    *) echo "No libcurl patch needed for version $libcurl_ver" ;;
esac

# Inject CXXFLAGS and fix linking
sed -i -e 's|-O3 -DNDEBUG|-DNDEBUG -DZEN_LINUX %{optflags}|g' \
       -e '/linkFlags/s|-s|%{__global_ldflags}|' \
    %{pkgname}/Source/Makefile \
    %{pkgname}/Source/%{prog2name}/Makefile

%build
%make_build -C %{pkgname}/Source
%make_build -C %{pkgname}/Source/%{prog2name}

%install
install -d %{buildroot}%{_bindir} %{buildroot}%{_datadir}/%{name}

pushd %{pkgname}/Build
install -m 0755 Bin/%{pkgname} Bin/%{prog2name} -t %{buildroot}%{_bindir}
cp -a Resources/* %{buildroot}%{_datadir}/%{name}
popd

# Ensure no scripts marked executable
find %{buildroot}%{_datadir}/%{name} -type f -exec chmod -x {} \;

# Desktop files
install -Dm0644 %{SOURCE1} %{buildroot}%{_datadir}/applications/%{pkgname}.desktop
install -Dm0644 %{SOURCE2} %{buildroot}%{_datadir}/applications/%{prog2name}.desktop

# MIME type XML
install -Dm0644 %{SOURCE3} %{buildroot}%{_datadir}/mime/packages/%{name}.xml

# Icons
unzip -j %{pkgname}/Build/Resources/Icons.zip -d .

ff=" -filter Lanczos"
for res in 16 22 24 32 48 64 96 128 256; do
    dir=%{buildroot}%{_datadir}/icons/hicolor/${res}x${res}
    rr=" -resize ${res}x${res}"
    mkdir -p ${dir}/apps ${dir}/mimetypes

    convert %{pkgname}.png ${ff} ${rr} ${dir}/apps/%{pkgname}.png
    convert %{prog2name}.png ${ff} ${rr} ${dir}/apps/%{prog2name}.png

    convert cfg_batch.png ${ff} ${rr} ${dir}/mimetypes/application-x-freefilesync-batch.png
    convert start_sync.png ${ff} ${rr} ${dir}/mimetypes/application-x-freefilesync-ffs.png
    convert %{prog2name}.png ${ff} ${rr} ${dir}/mimetypes/application-x-freefilesync-real.png
done

%post
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
if [ "$1" = 0 ]; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
fi

%posttrans
update-desktop-database &>/dev/null || :
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
update-mime-database -n %{_datadir}/mime &>/dev/null || :

%files
%license License.txt
%doc Changelog.txt
%{_bindir}/%{pkgname}
%{_bindir}/%{prog2name}
%{_datadir}/applications/%{pkgname}.desktop
%{_datadir}/applications/%{prog2name}.desktop
%{_datadir}/icons/hicolor/*x*/*/*.png
%{_datadir}/mime/packages/%{name}.xml
%{_datadir}/%{name}
%ghost %config(noreplace) %{_datadir}/%{name}/GlobalSettings.xml

%changelog
%autochangelog