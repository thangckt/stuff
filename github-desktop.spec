### This code with the help by Claude and ChatGPT

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

# Remove native modules that break build (not needed on Linux)
rm -rf vendor/desktop-notifications
rm -rf vendor/windows-argv-parser

# Clean from package.json and app/package.json
npm pkg delete dependencies.desktop-notifications || :
npm pkg delete dependencies.windows-argv-parser || :
npm pkg delete optionalDependencies.desktop-notifications || :

pushd app
npm pkg delete dependencies.desktop-notifications || :
npm pkg delete dependencies.windows-argv-parser || :
npm pkg delete optionalDependencies.desktop-notifications || :
popd

# Remove require lines from source
find app -type f -name '*.js' -exec sed -i '/desktop-notifications/d' {} \;
find app -type f -name '*.js' -exec sed -i '/windows-argv-parser/d' {} \;

# Remove postinstall-postinstall hook that breaks on CI
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

# Fix RPATHs
if [ -d "%{buildroot}%{_datadir}/%{name}/node_modules/dugite/git/libexec/git-core" ]; then
    find %{buildroot}%{_datadir}/%{name}/node_modules/dugite/git/libexec/git-core \
        -type f -exec chrpath --delete '{}' + 2>/dev/null || :
fi

# Launcher wrapper
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