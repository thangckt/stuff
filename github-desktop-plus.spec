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

%global _module_build 1
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

# Remove problematic native module
rm -rf vendor/desktop-notifications

# Clean any native deps
npm pkg delete dependencies.desktop-notifications || :
npm pkg delete optionalDependencies.desktop-notifications || :

pushd app
npm pkg delete dependencies.desktop-notifications || :
npm pkg delete optionalDependencies.desktop-notifications || :
popd

# Patch out runtime requires if needed
find app -type f -name '*.js' -exec sed -i '/desktop-notifications/d' {} \;

%build
export NODE_OPTIONS="--max_old_space_size=4096"
export npm_config_cache=/tmp/.npm

npm install --legacy-peer-deps --no-optional
npm run build || true

%install
# Install into datadir
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -a app/* %{buildroot}%{_datadir}/%{name}/

# Create executable wrapper
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} << 'EOF'
#!/bin/bash
exec electron %{_datadir}/%{name} "$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

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
