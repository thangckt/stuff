### REF: https://www.zotero.org/support/dev/client_coding/building_the_desktop_app
### building Zotero from source (dependences: nodejs, npm) is quite complex and may still have issues -> Use the official binary (Recommended)

Name:           zotero
Version:        7.0.19
Release:        1%{?dist}
Summary:        Zotero Reference Manager

License:        AGPL-3.0-only
URL:            https://www.zotero.org/
Source0:        https://download.zotero.org/client/release/%{version}/Zotero-%{version}_linux-x86_64.tar.bz2

ExclusiveArch:  x86_64
AutoReqProv:    no

# Disable debug package generation for binary packages
%global debug_package %{nil}

Requires:       gtk3 libXt libX11 dbus-glib

%description
Zotero is a free, easy-to-use tool to help you collect, organize, cite, and share research. This package contains the official Zotero binary.

%prep
%setup -q -n Zotero_linux-x86_64

%build
# Nothing to build - this is a binary package

%install
mkdir -p %{buildroot}/opt/zotero %{buildroot}%{_bindir} %{buildroot}%{_datadir}/applications %{buildroot}%{_datadir}/icons/hicolor/scalable/apps

# Install the application
cp -a * %{buildroot}/opt/zotero/

# Create wrapper script
cat > %{buildroot}%{_bindir}/zotero << 'EOF'
#!/bin/bash
exec /opt/zotero/zotero "$@"
EOF
chmod +x %{buildroot}%{_bindir}/zotero

# Create desktop file
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop << 'EOF'
[Desktop Entry]
Name=Zotero
Comment=Zotero Reference Manager
Exec=zotero
Icon=zotero
Type=Application
Categories=Office;Education;Science;
MimeType=text/plain;
EOF

# Copy icon
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
cp icons/icon128.png %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/zotero.png

%files
/opt/zotero
%{_bindir}/zotero
%{_datadir}/applications/zotero.desktop
%{_datadir}/icons/hicolor/scalable/apps/zotero.png

%changelog
%autochangelog