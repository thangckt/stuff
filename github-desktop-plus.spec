### This code with the help by Claude

Name:           github-desktop-plus
Version:        0.4.21
Release:        1%{?dist}
Summary:        GitHub Desktop Plus, a GUI client for Git and GitHub

License:        MIT
URL:            https://github.com/pol-rivero/github-desktop-plus
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

# Skip debug info for bundled binary
%global debug_package %{nil}

BuildRequires:  nodejs npm git python3 gcc-c++ make desktop-file-utils
Requires:       electron git

%description
GitHub Desktop Plus is a graphical Git client built on Electron for managing GitHub repositories easily.

%prep
%autosetup -n %{name}-%{version}

# Initialize dummy git repo (electron-builder needs it)
git init
git config user.email "rpm@localhost"
git config user.name "RPM Builder"
git add .
git commit -m "Initial commit"

# Remove problematic postinstall hook
npm pkg delete scripts.postinstall || :

%build
export PYTHON=/usr/bin/python3
export NODE_OPTIONS="--max_old_space_size=4096"
export npm_config_cache=/tmp/.npm

rm -rf node_modules app/node_modules
npm install --legacy-peer-deps --no-optional

# Build the Electron app
npx electron-builder --linux --dir

# Create launcher
cat > dist/linux-unpacked/%{name} << 'EOF'
#!/bin/bash
exec electron "$(dirname "$0")" "$@"
EOF
chmod +x dist/linux-unpacked/%{name}

%install
install -d %{buildroot}%{_datadir}/%{name}
cp -a dist/linux-unpacked/* %{buildroot}%{_datadir}/%{name}/

# Symlink binary
install -d %{buildroot}%{_bindir}
ln -s %{_datadir}/%{name}/%{name} %{buildroot}%{_bindir}/%{name}

# Install .desktop entry
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop << EOF
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
cp app/static/logos/icon-logo.ico %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.png || :

%files
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.png

%changelog
%autochangelog
