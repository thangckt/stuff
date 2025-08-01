### REF: https://gitlab.com/bgstack15/stackrpms/-/blob/master/freefilesync/freefilesync.spec?ref_type=heads
# - https://github.com/PhantomX/chinforpms/blob/main/_pasture/freefilesync/freefilesync.spec
# Note: wxWidgets>3.3 is required. It is better to build it in another spec file.

Name:       freefilesync
Version:    14.4
Release:    1%{?dist}
Summary:    A file synchronization utility
License:    GPLv3
URL:        http://www.freefilesync.org/

# upstream does not provide easy automatic downloads of the source, so use the mirror
#Source0:    http://www.freefilesync.org/download/%FreeFileSync_%%{version}_Source.zip
Source0:    https://gitlab.com/opensource-tracking/FreeFileSync/-/archive/%{version}/FreeFileSync-%{version}.tar.gz

%global debug_package %{nil}
%global _enable_debug_package 0
%global debugsource_package %{nil}
%global debugsource_build 0

BuildRequires:  gcc-c++ brotli-devel ImageMagick unzip patch
BuildRequires:  libcurl-devel libssh2-devel libselinux-devel
BuildRequires:  gtk3-devel gtk+-devel wxGTK-devel glib2-devel openssl-devel expat-devel
BuildRequires:  desktop-file-utils libmspack-devel libsecret-devel gspell-devel libnotify-devel webkit2gtk4.1-devel gstreamer1-devel
BuildRequires:  pkgconfig(liblzma) pkgconfig(libmspack) pkgconfig(libcurl) pkgconfig(libssh2) pkgconfig(glib-2.0) pkgconfig(zlib) pkgconfig(expat)
BuildRequires:  pkgconfig(giomm-2.4) pkgconfig(gtk+-3.0) pkgconfig(webkit2gtk-4.1) pkgconfig(libselinux) pkgconfig(libidn2)
BuildRequires:  wxGTK3 >= 3.3.0
Requires:       wxGTK3 >= 3.3.0

%description
FreeFileSync is an open-source software that helps synchronize files and folders on Windows, Linux, and macOS. It is optimized for backup speed and visual usability.

%prep
%setup -n FreeFileSync-%{version}

## Download and apply patches
custom_url="https://raw.githubusercontent.com/thangckt/stuff/refs/heads/copr_spec/patch/FreeFileSync"
patch_files=(
    "00_zen_string-traits_wxstring-support.patch"
    "01_zen_type-traits_cstdint.patch"
)
for file in "${patch_files[@]}"; do
    curl -L -o "$file" "$custom_url/$file"
    patch -p1 < "$file"
done


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

%build
export PATH=%{_bindir}:$PATH

## Ensure CXXFLAGS are passed directly to make, not just exported. The makefiles might not automatically pick up exported CXXFLAGS
export CXXFLAGS_FFS="$(pkg-config --cflags gtk+-3.0 glib-2.0 openssl libcurl libssh2 libselinux wxgtk3) -std=c++20 -I%{_builddir}/FreeFileSync-%{version} -I%{_builddir}/FreeFileSync-%{version}/zenXml"
export LDFLAGS_FFS="$(pkg-config --libs gtk+-3.0 openssl libcurl libssh2 libselinux wxgtk3)"

## Build FreeFileSync and RealTimeSync. Pass CXXFLAGS and LDFLAGS directly to make
%make_build -C FreeFileSync/Source CXXFLAGS="$CXXFLAGS_FFS" LDFLAGS="$LDFLAGS_FFS"
%make_build -C FreeFileSync/Source/RealTimeSync CXXFLAGS="$CXXFLAGS_FFS" LDFLAGS="$LDFLAGS_FFS"

echo "THA:-Debug: list binaries"
ls -l FreeFileSync/Build/Bin/
ls -l FreeFileSync/Build/


%install
# Manually install compiled binaries
install -Dm755 FreeFileSync/Build/Bin/FreeFileSync_x86_64 %{buildroot}%{_bindir}/FreeFileSync
install -Dm755 FreeFileSync/Build/Bin/RealTimeSync_x86_64 %{buildroot}%{_bindir}/RealTimeSync

# Install resource files used at runtime (icons, translations, config templates, etc.)
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -a FreeFileSync/Build/Resources/* %{buildroot}%{_datadir}/%{name}/

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
unzip -j FreeFileSync/Build/Resources/Icons.zip -d .
for res in 48 64 128; do
    dir=%{buildroot}%{_datadir}/icons/hicolor/${res}x${res}
    mkdir -p ${dir}/apps ${dir}/mimetypes
    magick convert FreeFileSync.png -filter Lanczos -resize ${res}x${res} ${dir}/apps/FreeFileSync.png
    magick convert RealTimeSync.png -filter Lanczos -resize ${res}x${res} ${dir}/apps/RealTimeSync.png
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
