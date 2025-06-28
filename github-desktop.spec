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

# Initialize dummy Git repo (some scripts need it)
git init
git config user.email "rpm@localhost"
git config user.name "RPM Builder"
git add .
git commit -m "Initial commit"

# Remove problematic native modules (non-Linux)
rm -rf vendor/desktop-notifications
rm -rf vendor/windows-argv-parser
rm -rf node_modules/registry-js

# Clean deps
npm pkg delete dependencies.desktop-notifications || :
npm pkg delete optionalDependencies.desktop-notifications || :
npm pkg delete dependencies.windows-argv-parser || :
npm pkg delete optionalDependencies.windows-argv-parser || :
npm pkg delete dependencies.registry-js || :

# Clean app subdir
pushd app
npm pkg delete dependencies.desktop-notifications || :
npm pkg delete dependencies.windows-argv-parser || :
npm pkg delete optionalDependencies.desktop-notifications || :
npm pkg delete optionalDependencies.windows-argv-parser || :
popd

# Remove import lines
find . -type f -name '*.js' -exec sed -i '/desktop-notifications/d;/windows-argv-parser/d;/registry-js/d' {} \;

# Remove postinstall script that fails in CI
npm pkg delete scripts.postinstall || :
npm pkg delete dependencies.postinstall-postinstall || :
rm -rf node_modules/postinstall-postinstall

%build
export NODE_OPTIONS="--max_old_space_size=4096"
export npm_config_cache=/tmp/.npm

npm install --legacy-peer-deps --omit=optional
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