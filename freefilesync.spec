### REF: https://gitlab.com/bgstack15/stackrpms/-/blob/master/freefilesync/freefilesync.spec?ref_type=heads
# - https://github.com/PhantomX/chinforpms/blob/main/_pasture/freefilesync/freefilesync.spec

Name:       freefilesync
Version:    14.4
Release:    1%{?dist}
Summary:    A file synchronization utility
License:    GPLv3
URL:        http://www.freefilesync.org/

# upstream does not provide easy automatic downloads of the source, so use the mirror
#Source0:    http://www.freefilesync.org/download/%FreeFileSync_%%{version}_Source.zip
Source0:    https://gitlab.com/opensource-tracking/FreeFileSync/-/archive/%{version}/FreeFileSync-%{version}.tar.gz
Source1:    https://github.com/wxWidgets/wxWidgets/releases/download/v3.3.1/wxWidgets-3.3.1.tar.bz2

BuildRequires:  gcc-c++ brotli-devel ImageMagick unzip
BuildRequires:  libcurl-devel libssh2-devel libselinux-devel
BuildRequires:  gtk3-devel gtk+-devel wxGTK-devel glib2-devel openssl-devel expat-devel
BuildRequires:  desktop-file-utils libmspack-devel libsecret-devel gspell-devel libnotify-devel webkit2gtk4.1-devel gstreamer1-devel
BuildRequires:  pkgconfig(zlib) pkgconfig(expat) pkgconfig(liblzma) pkgconfig(libmspack) pkgconfig(libcurl) pkgconfig(libssh2)
BuildRequires:  pkgconfig(giomm-2.4) pkgconfig(gtk+-3.0) pkgconfig(webkit2gtk-4.1) pkgconfig(libselinux) pkgconfig(glib-2.0) pkgconfig(libidn2)

Requires:       hicolor-icon-theme xdg-utils
Provides:       mimehandler(application/x-freefilesync-ffs)
Provides:       mimehandler(application/x-freefilesync-real)
Provides:       mimehandler(application/x-freefilesync-batch)

%description
FreeFileSync is an open-source software that helps synchronize files and folders on Windows, Linux, and macOS. It is optimized for backup speed and visual usability.

%global wxprefix %{_builddir}/wx33build

%prep
%setup -n FreeFileSync-%{version} -a 1

# Remove wxWidgets exception guard
sed -i '/#if wxUSE_EXCEPTIONS/,/#endif/d' FreeFileSync/Source/application.cpp
sed -i '/#if wxUSE_EXCEPTIONS/,/#endif/d' FreeFileSync/Source/RealTimeSync/application.cpp

# Remove hardcoded GTK2 usage from FreeFileSync makefile
sed -i 's/pkg-config --cflags gtk+-2.0//g' FreeFileSync/Source/Makefile
sed -i 's|-isystem/usr/include/gtk-2.0||g' FreeFileSync/Source/Makefile
sed -i 's/pkg-config --cflags gtk+-2.0//g' FreeFileSync/Source/RealTimeSync/Makefile
sed -i 's|-isystem/usr/include/gtk-2.0||g' FreeFileSync/Source/RealTimeSync/Makefile

# Fix undefined MAX_SFTP_* constants in afs/sftp.cpp
sed -i '1i#define MAX_SFTP_READ_SIZE 30000\n#define MAX_SFTP_OUTGOING_SIZE 30000' FreeFileSync/Source/afs/sftp.cpp

# Patch out use of wxColorHook for wxWidgets 3.3+
sed -i '/class SysColorsHook/,/^}/ s/^/\/\/ /' wx+/darkmode.cpp
sed -i '/refGlobalColorHook()/ s/^/\/\/ /' wx+/darkmode.cpp

## Build wxWidgets 3.3.1
tar xf %{SOURCE1}
pushd wxWidgets-3.3.1
mkdir buildgtk && cd buildgtk
../configure --prefix=%{wxprefix} --with-gtk=3 --enable-webview
make -j$(nproc)
make install
popd

%build
export PATH=%{wxprefix}/bin:$PATH
export WX_CONFIG=%{wxprefix}/bin/wx-config
export PKG_CONFIG_PATH=%{wxprefix}lib/pkgconfig:$PKG_CONFIG_PATH

# Add required flags
export CXXFLAGS="$($WX_CONFIG --cxxflags) $(pkg-config --cflags gtk+-3.0 glib-2.0 openssl libcurl libssh2 libselinux)"
export LDFLAGS="$($WX_CONFIG --libs) $(pkg-config --libs gtk+-3.0 openssl libcurl libssh2 libselinux)"

## Build FreeFileSync and RealTimeSync
echo "THA: building FreeFileSync"
%make_build -C FreeFileSync/Source
%make_build -C FreeFileSync/Source/RealTimeSync


echo "THA: install step"
%install
%make_install -C FreeFileSync/Source
%make_install -C FreeFileSync/Source/RealTimeSync

# Ensure no scripts marked executable
find %{buildroot}%{_datadir}/%{name} -type f -exec chmod -x {} \;

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
EOF

# Icons
unzip -j FreeFileSync/Build/Resources/Icons.zip -d .

ff=" -filter Lanczos"
for res in 16 22 24 32 48 64 96 128 256; do
    dir=%{buildroot}%{_datadir}/icons/hicolor/${res}x${res}
    rr=" -resize ${res}x${res}"
    mkdir -p ${dir}/apps ${dir}/mimetypes

    convert FreeFileSync.png ${ff} ${rr} ${dir}/apps/FreeFileSync.png
    convert RealTimeSync.png ${ff} ${rr} ${dir}/apps/RealTimeSync.png

    convert cfg_batch.png ${ff} ${rr} ${dir}/mimetypes/application-x-freefilesync-batch.png
    convert start_sync.png ${ff} ${rr} ${dir}/mimetypes/application-x-freefilesync-ffs.png
    convert RealTimeSync.png ${ff} ${rr} ${dir}/mimetypes/application-x-freefilesync-real.png
done


%files
%license License.txt
%doc Changelog.txt
%{_bindir}/FreeFileSync
%{_bindir}/RealTimeSync
%{_datadir}/applications/FreeFileSync.desktop
%{_datadir}/applications/RealTimeSync.desktop
%{_datadir}/icons/hicolor/*x*/*/*.png
%{_datadir}/%{name}

%changelog
%autochangelog
