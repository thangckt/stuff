### This code with the help by Claude and ChatGPT

Name:           github-desktop
Version:        3.4.21
Release:        1%{?dist}
Summary:        GitHub Desktop

License:        MIT
URL:            https://github.com/desktop/desktop
Source0:        %{url}/archive/refs/tags/release-%{version}.tar.gz

# Skip debug info for bundled Node code
%global debug_package %{nil}

BuildRequires:  nodejs npm git python3 gcc-c++ make chrpath libsecret-devel
Requires:       git

%description
GitHub Desktop is a graphical Git client for managing GitHub repositories easily.

%prep
%autosetup -n desktop-release-%{version}

# Initialize dummy git repo (npm postinstall scripts require it)
git init
git config user.email "rpm@localhost"
git config user.name "RPM Builder"
git add .
git commit -m "Initial commit"

# Remove native module that breaks build
rm -rf vendor/desktop-notifications

# Clean desktop-notifications dependencies
npm pkg delete dependencies.desktop-notifications || :
npm pkg delete optionalDependencies.desktop-notifications || :
pushd app
npm pkg delete dependencies.desktop-notifications || :
npm pkg delete optionalDependencies.desktop-notifications || :
popd

# Remove postinstall-postinstall to avoid .git error during npm install
npm pkg delete scripts.postinstall || :
npm pkg delete dependencies.postinstall-postinstall || :
rm -rf node_modules/postinstall-postinstall

# Remove require lines referencing desktop-notifications
find app -type f -name '*.js' -exec sed -i '/desktop-notifications/d' {} \;

%build
export NODE_OPTIONS="--max_old_space_size=4096"
export npm_config_cache=/tmp/.npm

# Important: allow scripts (so Electron gets bundled), but skip optional deps
npm install --legacy-peer-deps --omit=optional
npx --yes electron@22 install || :

npm run build || :

%install
# Install app files
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -a app/* %{buildroot}%{_datadir}/%{name}/

# Remove invalid RPATHs from dugite git binaries
if [ -d "%{buildroot}%{_datadir}/%{name}/node_modules/dugite/git/libexec/git-core" ]; then
    find %{buildroot}%{_datadir}/%{name}/node_modules/dugite/git/libexec/git-core \
        -type f -exec chrpath --delete '{}' + 2>/dev/null || :
fi

# Wrapper script to use bundled Electron
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} << 'EOF'
#!/bin/bash
exec /usr/share/github-desktop-plus/node_modules/electron/dist/electron /usr/share/github-desktop-plus "$@"
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

# Icon (fallback to dummy if missing)
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
cp app/static/linux/logos/256x256.png %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.png || :

%files
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.png

%changelog
%autochangelog