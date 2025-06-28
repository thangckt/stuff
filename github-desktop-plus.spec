### This code revise by Claude

Name: github-desktop
Version: 0.4.21
Release: 1%{?dist}
Summary: GitHub Desktop Plus, a GUI client for Git and GitHub

License: MIT
URL: https://github.com/pol-rivero/github-desktop-plus
Source0: %{url}/archive/refs/tags/v%{version}.tar.gz

# Disable debug package generation for binary packages
%global debug_package %{nil}

BuildRequires: nodejs npm git python3 gcc-c++ make desktop-file-utils
Requires: git

%description
GitHub Desktop Plus provides a GUI for Git and GitHub, simplifying cloning, committing, and pull requests on Linux.

%prep
%autosetup -n %{name}-%{version}

# Install deps
npm install --legacy-peer-deps

# Build the app
npx electron-builder --linux --dir

%install
# Install app into datadir
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -a dist/linux-unpacked/* %{buildroot}%{_datadir}/%{name}/

# Install launcher
mkdir -p %{buildroot}%{_bindir}
cat >%{buildroot}%{_bindir}/%{name} <<EOF
#!/bin/bash
exec %{_datadir}/%{name}/github-desktop "\$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

# Install .desktop entry
install -Dm644 /dev/stdin %{buildroot}%{_datadir}/applications/%{name}.desktop <<EOF
[Desktop Entry]
Name=GitHub Desktop
Comment=GitHub Desktop Plus - A Git GUI client for GitHub
GenericName=Git GUI Client
Exec=%{name}
Icon=%{name}
Type=Application
Terminal=false
Categories=Development;RevisionControl;
MimeType=x-scheme-handler/x-github-client;x-scheme-handler/x-github-desktop-auth;
EOF

# Install icon
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
icon_path="app/static/logos/icon-logo.ico"
cp "$icon_path" %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.png

%files
%{_datadir}/%{name}/
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.png

%changelog
%autochangelog
