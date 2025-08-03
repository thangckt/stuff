### REF: https://gitlab.com/bgstack15/stackrpms/-/blob/master/freefilesync/freefilesync.spec?ref_type=heads
# - https://github.com/PhantomX/chinforpms/blob/main/_pasture/freefilesync/freefilesync.spec
# Note: FreeFileSync 14.4 depends on wxWidgets>=3.3.0.

Name:       freefilesync
Version:    14.4
Release:    1%{?dist}
Summary:    A file synchronization utility
License:    GPLv3
URL:        http://www.freefilesync.org/

# upstream does not provide easy automatic downloads of the source, so use the mirror
# Source0:    http://www.freefilesync.org/download/%FreeFileSync_%%{version}_Source.zip
# Source0:    https://gitlab.com/opensource-tracking/FreeFileSync/-/archive/%{version}/FreeFileSync-%{version}.tar.gz
Source0:    https://github.com/hkneptune/FreeFileSync/archive/refs/tags/v%{version}.tar.gz

%global debug_package %{nil}
%global _enable_debug_package 0
%global debugsource_package %{nil}
%global debugsource_build 0

BuildRequires:  gcc-c++ unzip patch brotli-devel gettext-devel ImageMagick
BuildRequires:  wxGTK3 >= 3.3.0
# Use pkgconfig() where available to avoid duplicate raw -devel references
BuildRequires:  pkgconfig(libcurl) pkgconfig(libssh2) pkgconfig(libidn2) pkgconfig(libselinux)
BuildRequires:  pkgconfig(glib-2.0) pkgconfig(gtk+-3.0) pkgconfig(giomm-2.4) pkgconfig(webkit2gtk-4.1)
BuildRequires:  pkgconfig(gspell-1) pkgconfig(libsecret-1) pkgconfig(libmspack) pkgconfig(libnotify)
BuildRequires:  pkgconfig(liblzma) pkgconfig(expat) pkgconfig(zlib) pkgconfig(openssl) pkgconfig(gstreamer-1.0)

%description
FreeFileSync is an open-source software that helps synchronize files and folders on Windows, Linux, and macOS. It is optimized for backup speed and visual usability.

%prep
%setup -n FreeFileSync-%{version}

## Patch to remove wxWidgets exception guard
sed -i '/#if wxUSE_EXCEPTIONS/,/#endif/d' FreeFileSync/Source/application.cpp
sed -i '/#if wxUSE_EXCEPTIONS/,/#endif/d' FreeFileSync/Source/RealTimeSync/application.cpp

## Patch to remove hardcoded GTK2 usage from FreeFileSync makefile
sed -i 's/pkg-config --cflags gtk+-2.0//g' FreeFileSync/Source/Makefile
sed -i 's/pkg-config --cflags gtk+-2.0//g' FreeFileSync/Source/RealTimeSync/Makefile
sed -i 's|-isystem/usr/include/gtk-2.0||g' FreeFileSync/Source/Makefile
sed -i 's|-isystem/usr/include/gtk-2.0||g' FreeFileSync/Source/RealTimeSync/Makefile
sed -i 's| -lssh| -lssh -lidn2|' FreeFileSync/Source/Makefile
sed -i 's| -lssh| -lssh -lidn2|' FreeFileSync/Source/RealTimeSync/Makefile

## Fix undefined MAX_SFTP_* constants in afs/sftp.cpp
sed -i '1i#define MAX_SFTP_READ_SIZE 30000\n#define MAX_SFTP_OUTGOING_SIZE 30000' FreeFileSync/Source/afs/sftp.cpp

## Patch out use of wxColorHook for wxWidgets 3.3+
sed -i '/class SysColorsHook/,/^}/ s/^/\/\/ /' wx+/darkmode.cpp
sed -i '/refGlobalColorHook()/ s/^/\/\/ /' wx+/darkmode.cpp

## Patch `zen/scope_guard.h` to ensure <exception> is included and correct function is used.
sed -i '/#include "legacy_compiler.h"/a #include <exception>' zen/scope_guard.h
sed -i 's|std::uncaught_exception() ? 1 : 0|std::uncaught_exceptions()|g' zen/scope_guard.h
sed -i 's|std::uncaught_exceptions()|std::uncaught_exceptions()|g' zen/scope_guard.h
sed -i 's|std::uncaught_exceptions() > exeptionCount_|std::uncaught_exceptions() > exeptionCount_|g' zen/scope_guard.h

## Patch to fix uint32_t error in `zen/type_traits.h` and zen/argon2.h (include the <cstdint> header)
sed -i '1i#include <cstdint>' zen/type_traits.h
sed -i '1i#include <cstdint>' zen/argon2.h

## Patch base/algorithm.cpp to ensure warn_static is defined
sed -i '1i#include <exception>\n\
template<typename... T> void warn_static(const T&...) {}\n' FreeFileSync/Source/base/algorithm.cpp
sed -i "s|warn_static(\"TODO: some users want to manually fix renamed folders/files: combine them here, don't require a re-compare!\")|warn_static(\"TODO: some users want to manually fix renamed folders/files: combine them here, don't require a re-compare!\");|" FreeFileSync/Source/base/algorithm.cpp

## Patch base/db_file.h correctly for structured bindings and `inserted`
sed -i 's|files.emplace(fileName, InSyncFile {descrL, descrR, cmpVar, fileSize});|const auto [it, inserted] = files.emplace(fileName, InSyncFile {descrL, descrR, cmpVar, fileSize});|' FreeFileSync/Source/base/db_file.h
sed -i 's|symlinks.emplace(linkName, InSyncSymlink {descrL, descrR, cmpVar});|const auto [it, inserted] = symlinks.emplace(linkName, InSyncSymlink {descrL, descrR, cmpVar});|' FreeFileSync/Source/base/db_file.h

## Patch to fix incorrect isLocked() in base/synchronization.cpp and zen/stream_buffer.h (remove assert)
sed -i '/assert(isLocked(singleThread_));/d' FreeFileSync/Source/base/synchronization.cpp
sed -i '/assert(isLocked(lockStream_));/d' zen/stream_buffer.h

## Patch afs/abstract.cpp
sed -i '1i#include <zen/warn_static.h>' FreeFileSync/Source/afs/abstract.cpp
sed -i 's|auto attrSourceNew = attr ? \*attr : attrSource;|attrSourceNew = attr ? *attr : attrSource;|' FreeFileSync/Source/afs/abstract.cpp

## Patch ui/progress_indicator.cpp
sed -i '1i#include <zen/warn_static.h>' FreeFileSync/Source/ui/progress_indicator.cpp

## Fix memset error
sed -i '1i#include <cstring>' zen/argon2.cpp

## Fix Global<> in zen/file_path.cpp
sed -i '/#include "file_path.h"/a #include "globals.h"' zen/file_path.cpp

## Fix runningOnMainThread error (remove assert)
sed -i '/assert(runningOnMainThread());/d' zen/file_path.cpp

## Patch to change the Resources dir
sed -i '/Zstring fff::getResourceDirPath()/,/^}/c\
Zstring fff::getResourceDirPath()\
{\
    return Zstr("/usr/share/freefilesync/Resources");\
}' FreeFileSync/Source/ffs_paths.cpp

## Comment out GTK3 scrollbar assertion that fails at runtime
sed -i '/assert(scrollBarSizeTmp.y == 0 ||/,/scrollBarSizeTmp.y == 16);/ s/^/\/\//' wx+/grid.cpp


%build
export PATH=%{_bindir}:$PATH

## Ensure CXXFLAGS are passed directly to make, not just exported. The makefiles might not automatically pick up exported CXXFLAGS
export CXXFLAGS_FFS="%{optflags} $(pkg-config --cflags gtk+-3.0 glib-2.0 openssl libcurl libssh2 libselinux wxgtk3) -I%{_builddir}/FreeFileSync-%{version} -I%{_builddir}/FreeFileSync-%{version}/zenXml -std=c++23 -DWXINTL_NO_GETTEXT_MACRO"
export LDFLAGS_FFS="$(pkg-config --libs gtk+-3.0 glib-2.0 openssl libcurl libssh2 libselinux wxgtk3) -lidn2"

## Build FreeFileSync and RealTimeSync. Pass CXXFLAGS and LDFLAGS directly to make
%make_build -C FreeFileSync/Source CXXFLAGS="$CXXFLAGS_FFS" LDFLAGS="$LDFLAGS_FFS"
%make_build -C FreeFileSync/Source/RealTimeSync CXXFLAGS="$CXXFLAGS_FFS" LDFLAGS="$LDFLAGS_FFS"

echo "#ANCHOR: list binaries"
ls -l FreeFileSync/Build/Bin/
ls -l FreeFileSync/Build/


%install
## Manually install compiled binaries
install -Dm755 FreeFileSync/Build/Bin/FreeFileSync_x86_64 %{buildroot}%{_bindir}/FreeFileSync
install -Dm755 FreeFileSync/Build/Bin/RealTimeSync_x86_64 %{buildroot}%{_bindir}/RealTimeSync

##ANCHOR: Install resource files used at runtime (icons, translations, config templates, etc.)
mkdir -p %{buildroot}%{_datadir}/%{name}/Resources/
cp -a FreeFileSync/Build/Resources/* %{buildroot}%{_datadir}/%{name}/Resources/
unzip -j %{buildroot}%{_datadir}/%{name}/Resources/Icons.zip -d %{buildroot}%{_datadir}/%{name}/Resources/

# mkdir - %{buildroot}/usr/Resources/
# cp -a FreeFileSync/Build/Resources/* %{buildroot}/usr/Resources/

## Ensure no scripts marked executable
find %{buildroot}%{_datadir}/%{name} -type f -exec chmod -x '{}' \; || :

## Desktop files
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/FreeFileSync.desktop <<EOF
[Desktop Entry]
Name=FreeFileSync
GenericName=File synchronization
Exec=FreeFileSync
Icon=FreeFileSync
Terminal=false
Type=Application
StartupNotify=true
Categories=Utility;
MimeType=application/x-freefilesync-ffs;application/x-freefilesync-batch;
EOF

cat > %{buildroot}%{_datadir}/applications/RealTimeSync.desktop <<EOF
[Desktop Entry]
Name=RealTimeSync
GenericName=Automated Synchronization
Exec=RealTimeSync
Icon=RealTimeSync
Terminal=false
Type=Application
StartupNotify=true
Categories=Utility;
MimeType=application/x-freefilesync-real;
EOF

## Icons
unzip -j FreeFileSync/Build/Resources/Icons.zip -d tmp_icons
for res in 16 22 24 32 48 64 96 128 ;do
    dir=%{buildroot}%{_datadir}/icons/hicolor/${res}x${res}
    mkdir -p ${dir}/apps
    magick tmp_icons/FreeFileSync.png -filter Lanczos -resize ${res}x${res} ${dir}/apps/FreeFileSync.png
    magick tmp_icons/RealTimeSync.png -filter Lanczos -resize ${res}x${res} ${dir}/apps/RealTimeSync.png
done
rm -rf tmp_icons


%files
%license License.txt
%doc Changelog.txt
%{_bindir}/FreeFileSync
%{_bindir}/RealTimeSync
%{_datadir}/applications/FreeFileSync.desktop
%{_datadir}/applications/RealTimeSync.desktop
%{_datadir}/icons/hicolor/*x*/*/*.png
%{_datadir}/%{name}
# /usr/Resources/*

%changelog
%autochangelog
