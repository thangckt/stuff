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

# Required dummy repo
git init
git config user.email "rpm@localhost"
git config user.name "RPM Builder"
git add .
git commit -m "init"

# Patch webpack config to skip highlighter target
sed -i '/highlighter/d' app/webpack.production.ts

# Remove native modules that break build
rm -rf vendor/desktop-notifications
rm -rf node_modules/postinstall-postinstall
rm -rf app/node_modules/desktop-notifications

# Remove from root package.json
sed -i '/"desktop-notifications"/d' package.json
sed -i '/"postinstall-postinstall"/d' package.json
sed -i '/"postinstall":/d' package.json
sed -i '/"prepare":/d' package.json
sed -i '/"preinstall":/d' package.json
sed -i '/"install":/d' package.json

# Remove build:prod references to yarn
sed -i 's/yarn compile:prod/npm run compile:prod/' package.json
sed -i 's/yarn/npm run/g' package.json

# Same fix in app/package.json
pushd app
sed -i '/"desktop-notifications"/d' package.json
sed -i '/"postinstall-postinstall"/d' package.json
sed -i '/"postinstall":/d' package.json
sed -i '/"prepare":/d' package.json
sed -i '/"preinstall":/d' package.json
sed -i '/"install":/d' package.json
sed -i 's/yarn compile:prod/npm run compile:prod/' package.json
sed -i 's/yarn/npm run/g' package.json

# Set safe electron version
sed -i 's#"electron":.*#"electron": "^22.0.0",#' package.json
popd

# Remove all yarn calls in TS/JS files
find . -type f \( -name '*.js' -o -name '*.ts' \) -exec sed -i '/yarn/d' {} \;

# Disable telemetry
echo "DESKTOP_DISABLE_TELEMETRY=1" > .env.production

%build
export NODE_OPTIONS="--max_old_space_size=4096"
export NODE_ENV=production
export TS_NODE_PROJECT=script/tsconfig.json
export npm_config_cache=/tmp/.npm

npm install --legacy-peer-deps --omit=optional
npm run build:prod

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