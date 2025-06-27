### This code revise by Claude

Name: github-desktop-plus
Version: 0.4.21
Release: 1%{?dist}
Summary: GitHub Desktop Plus, a GUI client for Git and GitHub

License: MIT
URL: https://github.com/pol-rivero/github-desktop-plus
Source0: %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

# Disable debug package generation for binary packages
%global debug_package %{nil}

BuildRequires: nodejs npm git python3 gcc-c++ make desktop-file-utils
Requires: git

%description
GitHub Desktop Plus provides a GUI for Git and GitHub, simplifying cloning, committing, and pull requests on Linux.

%prep
%autosetup -n %{name}-%{version}

# Create minimal git repo (required by some build scripts)
git init
git config user.email "builder@localhost"
git config user.name "RPM Builder"
git add .
git commit -m "Initial commit for build"

%build
# Ensure clean build
rm -rf node_modules package-lock.json app/node_modules app/package-lock.json

# Remove problematic deps
sed -i 's/"postinstall-postinstall".*,//g' package.json app/package.json 2>/dev/null || true
sed -i 's/"@types\/glob".*,//g' package.json app/package.json 2>/dev/null || true

# Set safe tsconfig
cat >tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "skipLibCheck": true,
    "allowJs": true,
    "noEmitOnError": false
  }
}
EOF

# Install deps
npm install --legacy-peer-deps --no-scripts --ignore-scripts --no-audit --no-fund

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
exec %{_datadir}/%{name}/github-desktop-plus "\$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

# Install .desktop entry
mkdir -p %{buildroot}%{_datadir}/applications
cat >%{buildroot}%{_datadir}/applications/%{name}.desktop <<EOF
[Desktop Entry]
Name=GitHub Desktop Plus
Comment=GitHub Desktop Plus - A Git GUI client for GitHub
GenericName=Git GUI Client
Exec=%{_bindir}/%{name}
Icon=%{name}
Type=Application
StartupNotify=true
Categories=Development;RevisionControl;
Keywords=git;github;version control;development;
MimeType=x-scheme-handler/x-github-client;x-scheme-handler/x-github-desktop-auth;
StartupWMClass=GitHub Desktop
EOF

# Install icon
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/256x256/apps
icon_path="app/static/logos/icon-logo.png"
if [ -f "$icon_path" ]; then
    cp "$icon_path" %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/%{name}.png
else
    echo "Warning: Icon not found!"
fi

%post
update-desktop-database &>/dev/null || :
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%postun
update-desktop-database &>/dev/null || :
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files
%{_datadir}/%{name}/
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/256x256/apps/%{name}.png

%changelog
%autochangelog
