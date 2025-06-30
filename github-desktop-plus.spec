### This code with the help by Claude and ChatGPT

Name:           github-desktop-plus
Version:        3.5.0
Release:        1%{?dist}
Summary:        GitHub Desktop Plus

License:        MIT
URL:            https://github.com/pol-rivero/github-desktop-plus
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

# Skip debug info for bundled Node code
%global debug_package %{nil}

BuildRequires: nodejs npm git python3 gcc-c++ make chrpath libsecret-devel
Requires:       git

%description
GitHub Desktop Plus is a graphical Git client for managing GitHub repositories easily.

%prep
%autosetup -n %{name}-%{version}

# Initialize dummy git repo (build expects one)
git init
git config user.email "rpm@localhost"
git config user.name "RPM Builder"
git add .
git commit -m "Initial commit"

# Install yarn locally in project (avoid global and corepack)
npm install yarn@1.22.19 --legacy-peer-deps --no-save

# Remove native module that breaks build
rm -rf vendor/desktop-notifications

# Remove all references to desktop-notifications
./node_modules/.bin/yarn remove desktop-notifications || :
pushd app
../node_modules/.bin/yarn remove desktop-notifications || :
popd
find app -type f -name '*.js' -exec sed -i '/desktop-notifications/d' {} \;

# Ensure Electron version compatible with Fedora Node.js
pushd app
../node_modules/.bin/yarn add electron@22 --dev
popd

# Create minimal .env.production if needed
echo "DESKTOP_DISABLE_TELEMETRY=1" > .env.production

%build
export NODE_OPTIONS="--max_old_space_size=4096"
export NODE_ENV=production
export TS_NODE_PROJECT=script/tsconfig.json
export npm_config_cache=/tmp/.npm

# Use local yarn binary
./node_modules/.bin/yarn install --ignore-optional --frozen-lockfile --legacy-peer-deps
./node_modules/.bin/yarn build:prod

%install
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -a app/* %{buildroot}%{_datadir}/%{name}/

# Remove invalid RPATHs from dugite git binaries
if [ -d "%{buildroot}%{_datadir}/%{name}/node_modules/dugite/git/libexec/git-core" ]; then
    find %{buildroot}%{_datadir}/%{name}/node_modules/dugite/git/libexec/git-core \
        -type f -exec chrpath --delete '{}' + 2>/dev/null || :
fi

# Launcher script
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} << 'EOF'
#!/bin/bash
exec %{_datadir}/%{name}/node_modules/electron/dist/electron %{_datadir}/%{name} "$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

# Desktop entry
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

# Icon
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
cp app/static/linux/logos/128x128.png %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.png || \
    convert -size 128x128 xc:gray %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.png

%files
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.png

%changelog
%autochangelog