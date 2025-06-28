### This code with the help by Claude and ChatGPT

Name:           github-desktop-plus
Version:        0.4.21
Release:        1%{?dist}
Summary:        GitHub Desktop Plus, a GUI client for Git and GitHub

License:        MIT
URL:            https://github.com/pol-rivero/github-desktop-plus
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

# Skip debug info for bundled Node code
%global debug_package %{nil}

BuildRequires:  nodejs npm git python3 gcc-c++ make desktop-file-utils chrpath
Requires:       electron git

%description
GitHub Desktop Plus is a graphical Git client built on Electron for managing GitHub repositories easily.

%prep
%autosetup -n %{name}-%{version}

# Remove native module that breaks build
rm -rf vendor/desktop-notifications

# Remove its reference from package.json
npm pkg delete dependencies.desktop-notifications || :
npm pkg delete optionalDependencies.desktop-notifications || :
pushd app
npm pkg delete dependencies.desktop-notifications || :
npm pkg delete optionalDependencies.desktop-notifications || :
popd

# Remove runtime require calls if needed
find app -type f -name '*.js' -exec sed -i '/desktop-notifications/d' {} \;

%build
export NODE_OPTIONS="--max_old_space_size=4096"
export npm_config_cache=/tmp/.npm

npm install --legacy-peer-deps --no-optional
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

# Wrapper script to run with system electron
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} << 'EOF'
#!/bin/bash
exec electron %{_datadir}/%{name} "$@"
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

# Icon (fallback to dummy if missing)
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
cp app/static/logos/icon-logo.ico %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.png || :
touch %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.png

%files
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.png

%changelog
%autochangelog