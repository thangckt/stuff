### This code revose with ChatGPT
### The souce code is not supported Linux

Name:           github-desktop
Version:        3.5.0
Release:        1%{?dist}
Summary:        GitHub Desktop

License:        MIT
URL:            https://github.com/desktop/desktop
Source0:        %{url}/archive/refs/tags/release-%{version}.tar.gz

%global debug_package %{nil}

BuildRequires:  nodejs npm yarnpkg git python3 gcc-c++ make chrpath libsecret-devel curl
Requires:       git

%description
GitHub Desktop is a graphical Git client for managing GitHub repositories easily.

%prep
%autosetup -n desktop-release-%{version}

# Initialize dummy Git repo for tooling that requires it
git init
git config user.email "rpm@localhost"
git config user.name "RPM Builder"
git add .
git commit -m "Initial commit"

# Remove native or Windows/macOS-only modules
rm -rf vendor/desktop-notifications vendor/windows-argv-parser node_modules/registry-js
rm -f app/src/lib/editors/win32.ts app/src/lib/editors/darwin.ts

# Clean up root package.json
npm pkg delete dependencies.desktop-notifications\*
npm pkg delete dependencies.windows-argv-parser\*
npm pkg delete dependencies.registry-js\*
npm pkg delete dependencies.dugite\*
npm pkg delete dependencies.app-path\*
npm pkg delete dependencies.postinstall-postinstall
npm pkg delete scripts.postinstall || :

# Clean app package.json
pushd app
npm pkg delete dependencies.desktop-notifications\*
npm pkg delete dependencies.windows-argv-parser\*
npm pkg delete dependencies.app-path\*
npm pkg delete dependencies.dugite\*
popd

# Remove imports referencing deleted modules
find app/src -type f -name '*.ts' -exec sed -i \
  -e "/desktop-notifications/d" \
  -e "/windows-argv-parser/d" \
  -e "/app-path/d" \
  -e "/dugite/d" \
  -e "/win32/d" \
  -e "/darwin/d" '{}' \;

# Fix broken multi-line import that causes build crash
sed -i '/getNotificationsPermission.*initializeDesktopNotifications/d' app/src/lib/editors/win32.ts 2>/dev/null || :

# Install CodeMirror + custom modes
npm install codemirror@5.65.12 codemirror-mode-luau codemirror-mode-zig --legacy-peer-deps

# Add type stubs
mkdir -p types
cat > types/custom.d.ts <<EOF
declare module 'codemirror-mode-luau';
declare module 'codemirror-mode-zig';
EOF

# Patch tsconfig
sed -i '/"exclude": \[/a \    "types/custom.d.ts",' script/tsconfig.json
sed -i 's/"strict": true/"strict": false/' script/tsconfig.json
sed -i '/"target":/a\  "skipLibCheck": true,\n  "noImplicitAny": false,' script/tsconfig.json

%build
export NODE_OPTIONS="--max_old_space_size=4096"
export npm_config_cache=/tmp/.npm

# Install only required deps (Linux-safe)
npm install ajv@6 ajv-keywords@3 \
  mem string-argv compare-versions dexie \
  --legacy-peer-deps
npm install --legacy-peer-deps --omit=optional
npm run build:prod

%install
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -a out/* %{buildroot}%{_datadir}/%{name}/

mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} <<EOF
#!/bin/bash
exec %{_datadir}/%{name}/github-desktop "\$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop << EOF
[Desktop Entry]
Name=GitHub Desktop
GenericName=Git GUI Client
Exec=%{name}
Icon=%{name}
Type=Application
Terminal=false
Categories=Development;RevisionControl;
EOF

mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
cp app/static/linux/icon-logo.png %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.png

%files
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.png

%changelog
%autochangelog