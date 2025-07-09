Name:           github-desktop
Version:        3.5.1
Release:        1%{?dist}
Summary:        GitHub Desktop Plus

License:        MIT
URL:            https://github.com/pol-rivero/github-desktop-plus
Source0:        %{url}/releases/download/v%{version}/GitHubDesktopPlus-v%{version}-linux-x86_64.rpm

ExclusiveArch:  x86_64
BuildRequires: nodejs npm
Requires:       git

%description
GitHub Desktop Plus (prebuilt binary). This package simply repackages the RPM for distribution via Copr.

%prep
# Nothing to do

%build
# Nothing to build

%install
mkdir -p %{buildroot}
rpm2cpio %{SOURCE0} | cpio -idmv -D %{buildroot}

# Remove broken internal git
rm -rf %{buildroot}/usr/lib/%{name}/resources/app/git

# Extract app.asar and patch dugite
npm install -g asar
export PATH=$PATH:$(npm bin -g)
cd %{buildroot}/usr/lib/%{name}/resources/
asar extract app.asar app_unpacked

# Patch resolveGitBinary
find app_unpacked -type f -name '*.js' -exec \
    sed -i 's|resolveGitBinary() *{[^}]*}|resolveGitBinary() { return "/usr/bin/git"; }|' {} +

# Repack the modified archive
rm -f app.asar
asar pack app_unpacked app.asar
rm -rf app_unpacked

%files
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
/usr/lib/%{name}/**
/usr/share/doc/%{name}/copyright

%changelog
%autochangelog
