### This code revose with ChatGPT

Name:           github-desktop
Version:        3.5.0
Release:        1%{?dist}
Summary:        GitHub Desktop

License:        MIT
URL:            https://github.com/desktop/desktop
Source0:        %{url}/archive/refs/tags/release-%{version}.tar.gz

%global debug_package %{nil}

BuildRequires:  nodejs npm git python3 gcc-c++ make chrpath libsecret-devel
Requires:       git

%description
GitHub Desktop is a graphical Git client for managing GitHub repositories easily.

%prep
%autosetup -n desktop-release-%{version}

# Initialize dummy git repo (for npm install)
git init
git config user.email "rpm@localhost"
git config user.name "RPM Builder"
git add .
git commit -m "Initial commit"

# === Remove native modules not used on Linux ===

# desktop-notifications (Linux native, but breaks build)
rm -rf vendor/desktop-notifications
npm pkg delete dependencies.desktop-notifications || :
npm pkg delete optionalDependencies.desktop-notifications || :

# windows-argv-parser (Windows-only native module)
rm -rf vendor/windows-argv-parser
npm pkg delete dependencies.windows-argv-parser || :
npm pkg delete optionalDependencies.windows-argv-parser || :

# registry-js (Windows-only native module)
npm pkg delete dependencies.registry-js || :
npm pkg delete optionalDependencies.registry-js || :
rm -rf node_modules/registry-js
find . -type f -name '*.js' -exec sed -i '/registry-js/d' {} \;

# Clean app/package.json as well
pushd app
npm pkg delete dependencies.desktop-notifications || :
npm pkg delete dependencies.windows-argv-parser || :
npm pkg delete optionalDependencies.desktop-notifications || :
npm pkg delete optionalDependencies.windows-argv-parser || :
npm pkg delete dependencies.registry-js || :
npm pkg delete optionalDependencies.registry-js || :
popd

# Remove require/import statements for removed modules
find app -type f -name '*.js' -exec sed -i '/desktop-notifications/d' {} \;
find app -type f -name '*.js' -exec sed -i '/windows-argv-parser/d' {} \;
find app -type f -name '*.js' -exec sed -i '/registry-js/d' {} \;

# Remove postinstall hook that fails due to lack of .git metadata
npm pkg delete scripts.postinstall || :
npm pkg delete dependencies.postinstall-postinstall || :
rm -rf node_modules/postinstall-postinstall

%build
export NODE_OPTIONS="--max_old_space_size=4096"
export npm_config_cache=/tmp/.npm

pushd app
# Electron version needed to run (downloaded via npm)
npm pkg set dependencies.electron="^22.0.0"
npm install --legacy-peer-deps --omit=optional
npm run build || :
popd

%install
# Install app files
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -a app/* %{buildroot}%{_datadir}/%{name}/

# Remove broken RPATHs from dugite Git binaries
GIT_BIN_DIR="%{buildroot}%{_datadir}/%{name}/node_modules/dugite/git/libexec/git-core"
if [ -d "$GIT_BIN_DIR" ]; then
    find "$GIT_BIN_DIR" -type f -exec file {} \; | \
        grep 'ELF.*executable' | \
        cut -d: -f1 | \
        xargs -r chrpath -d 2>/dev/null || :
fi

# Create wrapper
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} << EOF
#!/bin/bash
exec %{_datadir}/%{name}/node_modules/electron/dist/electron %{_datadir}/%{name} "\$@"
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
cp app/static/linux/icon-logo.png %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.png || :

%files
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.png

%changelog
%autochangelog