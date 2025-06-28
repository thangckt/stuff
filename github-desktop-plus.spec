### This code with the help by Claude

Name: github-desktop-plus
Version: 0.4.21
Release: 1%{?dist}
Summary: GitHub Desktop Plus, a GUI client for Git and GitHub

License:    MIT
URL:        https://github.com/pol-rivero/github-desktop-plus
Source0:    %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

# Disable debug package generation for binary packages
%global debug_package %{nil}

BuildRequires: nodejs npm git python3 gcc-c++ make desktop-file-utils jq
Requires: git electron

%description
GitHub Desktop Plus provides a GUI for Git and GitHub, simplifying cloning, committing, and pull requests on Linux.

%prep
%autosetup -n %{name}-%{version}

# Initialize a minimal git repo to satisfy build requirements
git init
git config user.email "builder@localhost"
git config user.name "RPM Builder"
git add .
git commit -m "Initial commit for build"

# Patch package.json files to remove problematic native dependencies
if [ -f "app/package.json" ]; then
    # Remove desktop-notifications dependency that's causing issues
    jq 'del(.dependencies["desktop-notifications"]) | del(.optionalDependencies["desktop-notifications"])' app/package.json > app/package.json.tmp
    mv app/package.json.tmp app/package.json
fi

%build
# Set environment for Node.js build
export PYTHON=/usr/bin/python3
export NODE_OPTIONS="--max_old_space_size=4096"
export npm_config_cache=/tmp/.npm

# Clean any existing node_modules and package-lock.json
rm -rf node_modules package-lock.json app/node_modules app/package-lock.json

# Install dependencies without optional/problematic packages
npm install --legacy-peer-deps --no-optional

# Build the app using system electron
npx electron-builder --linux --dir --config.electronDist=/usr/share/electron --config.electronVersion=$(electron --version | sed 's/v//')

%install
# Install app into datadir
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -a dist/linux-unpacked/* %{buildroot}%{_datadir}/%{name}/

# Create executable wrapper in bindir that uses system electron
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} << 'EOF'
#!/bin/bash
exec electron %{_datadir}/%{name} "$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

# Install .desktop entry
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop << 'EOF'
[Desktop Entry]
Name=GitHub Desktop+
GenericName=Git GUI Client
Exec=%{name}
Icon=%{name}
Type=Application
Terminal=false
Categories=Development;RevisionControl;
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
