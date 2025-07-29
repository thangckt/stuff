### REF: https://gitlab.com/bgstack15/stackrpms/-/blob/master/freefilesync/freefilesync.spec?ref_type=heads

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

%global patch_base_url https://gitlab.com/bgstack15/stackrpms/-/raw/master/freefilesync

BuildRequires:  gcc-c++ brotli-devel ImageMagick unzip
BuildRequires:  desktop-file-utils patch
BuildRequires:  pkgconfig(giomm-2.4) pkgconfig(gtk+-3.0) pkgconfig(gtk+-2.0) pkgconfig(zlib)
BuildRequires:  libcurl-devel libssh2-devel libselinux-devel
BuildRequires:  gtk+-devel gtk2-devel wxGTK-devel glib2-devel openssl openssl-devel

Requires:       hicolor-icon-theme xdg-utils
Provides:       mimehandler(application/x-freefilesync-ffs)
Provides:       mimehandler(application/x-freefilesync-real)
Provides:       mimehandler(application/x-freefilesync-batch)

%description
FreeFileSync is an open-source software that helps synchronize files and folders on Windows, Linux, and macOS.
It is optimized for backup speed and visual usability.

%prep
%setup -n %{pkgname}-%{version}

# Embed patch inline to bypass wxWidgets exception guard
cat > allow-wx-exceptions.patch << 'EOF'
diff --git a/FreeFileSync/Source/application.cpp b/FreeFileSync/Source/application.cpp
index 1234567..89abcde 100644
--- a/FreeFileSync/Source/application.cpp
+++ b/FreeFileSync/Source/application.cpp
@@ -240,9 +240,6 @@
     #include <wx/msw/private.h>
 #endif

-#if wxUSE_EXCEPTIONS
-#error why is wxWidgets uncaught exception handling enabled!?
-#endif
EOF

%patch -p1 < allow-wx-exceptions.patch


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
install -Dm0644 "%{patch_base_url}/FreeFileSync.desktop" %{buildroot}%{_datadir}/applications/FreeFileSync.desktop
install -Dm0644 "%{patch_base_url}/RealTimeSync.desktop" %{buildroot}%{_datadir}/applications/RealTimeSync.desktop

# MIME type XML
install -Dm0644 "%{patch_base_url}/xml.desktop" %{buildroot}%{_datadir}/mime/packages/freefilesync.xml

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