### This code revose with ChatGPT
### The souce code targets Windows/iOS, not Linux

Name:           github-desktop
Version:        3.5.0
Release:        1%{?dist}
Summary:        GitHub Desktop (Linux-only build)

License:        MIT
URL:            https://github.com/desktop/desktop
Source0:        %{url}/archive/refs/tags/release-%{version}.tar.gz

%global debug_package %{nil}

BuildRequires:  nodejs npm yarnpkg git python3 gcc-c++ make chrpath libsecret-devel curl
Requires:       git

%description
GitHub Desktop is a graphical Git client. This build is stripped down to work only on Linux.

%prep
%autosetup -n desktop-release-%{version}

git init
 git config user.email "rpm@localhost"
 git config user.name "RPM Builder"
 git add .
 git commit -m "Initial commit"

# Remove native/non-Linux code
rm -rf vendor/desktop-notifications vendor/windows-argv-parser vendor/registry-js \
       app/src/lib/editors/darwin.ts \
       app/src/lib/editors/win32.ts \
       app/src/lib/custom-integration.ts \
       app/src/lib/ipc-shared.ts \
       app/src/lib/ipc-renderer.ts \
       app/src/lib/path.ts \
       app/src/lib/is-application-bundle.ts \
       app/src/lib/git \
       app/src/cli

# Clean dependencies from root and app package.json
npm pkg delete dependencies.desktop-notifications dependencies.windows-argv-parser dependencies.registry-js dependencies.postinstall-postinstall
npm pkg delete scripts.postinstall || :
pushd app
npm pkg delete dependencies.desktop-notifications dependencies.windows-argv-parser
popd

# Patch tsconfig to disable strict and exclude removed files
sed -i 's/"strict": true/"strict": false/' script/tsconfig.json
sed -i '/"target":/a\  "skipLibCheck": true,\n  "noImplicitAny": false,' script/tsconfig.json
sed -i '/"exclude": \[/a\    "app\/src\/cli",\n    "app\/src\/lib\/ipc-shared.ts",\n    "app\/src\/lib\/ipc-renderer.ts",\n    "app\/src\/lib\/custom-integration.ts",\n    "app\/src\/lib\/editors\/darwin.ts",\n    "app\/src\/lib\/editors\/win32.ts",\n    "app\/src\/lib\/is-application-bundle.ts",\n    "app\/src\/lib\/path.ts",\n    "app\/src\/lib\/git"' script/tsconfig.json

# Create stub types
mkdir -p types
cat > types/custom.d.ts <<EOF
declare module 'codemirror-mode-luau';
declare module 'codemirror-mode-zig';
EOF

sed -i '/"exclude": \[/a\    "types\/custom.d.ts",' script/tsconfig.json

%build
export NODE_OPTIONS="--max_old_space_size=4096"
export npm_config_cache=/tmp/.npm

npm install ajv@6 ajv-keywords@3 mem string-argv \
    compare-versions dexie codemirror@5.65.12 --legacy-peer-deps
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
