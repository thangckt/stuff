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

BuildRequires:  nodejs npm yarnpkg git python3 gcc-c++ make chrpath libsecret-devel
Requires:       git

%description
GitHub Desktop is a graphical Git client for managing GitHub repositories easily.

%prep
%autosetup -n desktop-release-%{version}

# Initialize dummy Git repo
git init
git config user.email "rpm@localhost"
git config user.name "RPM Builder"
git add .
git commit -m "Initial commit"

# Remove problematic native modules
rm -rf vendor/desktop-notifications
rm -rf vendor/windows-argv-parser
rm -rf node_modules/registry-js

# Clean up root package.json
npm pkg delete dependencies.desktop-notifications || :
npm pkg delete optionalDependencies.desktop-notifications || :
npm pkg delete dependencies.windows-argv-parser || :
npm pkg delete optionalDependencies.windows-argv-parser || :
npm pkg delete dependencies.registry-js || :
npm pkg delete dependencies.postinstall-postinstall || :
npm pkg delete scripts.postinstall || :

# Clean up app/package.json
pushd app
npm pkg delete dependencies.desktop-notifications || :
npm pkg delete optionalDependencies.desktop-notifications || :
npm pkg delete dependencies.windows-argv-parser || :
npm pkg delete optionalDependencies.windows-argv-parser || :
popd

# Remove imports in source code for removed modules
find . -type f -name '*.js' -exec sed -i '/desktop-notifications/d;/windows-argv-parser/d;/registry-js/d' {} \;

# Add custom type stubs
mkdir -p types
cat > types/custom.d.ts <<'EOF'
// Stub modules missing type declarations
declare module 'codemirror-mode-luau';
declare module 'codemirror-mode-zig';
declare module 'codemirror-mode-elixir';
EOF

# Patch tsconfig to include type stubs
sed -i '/"exclude": \[/a\    "types/custom.d.ts",' script/tsconfig.json
sed -i 's/"strict": true/"strict": false/' script/tsconfig.json
sed -i '/"target":/a\  "skipLibCheck": true,' script/tsconfig.json

%build
export NODE_OPTIONS="--max_old_space_size=4096"
export npm_config_cache=/tmp/.npm

# Install all dependencies including CodeMirror + missing modes
npm install --legacy-peer-deps --omit=optional

# Install codemirror + extra language modes
npm install codemirror@5 --legacy-peer-deps
npm install git+https://github.com/Roblox/codemirror-luau-mode.git || :
npm install git+https://github.com/marzer/codemirror-mode-zig.git || :

# Continue with build
npm run build:prod

%install
# Copy full app output
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -a out/* %{buildroot}%{_datadir}/%{name}/

# Create launcher script
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} << EOF
#!/bin/bash
exec %{_datadir}/%{name}/github-desktop "\$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

# Desktop entry
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

# Icon
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
cp app/static/linux/icon-logo.png %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.png

%files
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.png

%changelog
%autochangelog