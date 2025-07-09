Name:           github-desktop
Version:        3.5.1
Release:        1%{?dist}
Summary:        GitHub Desktop Plus

License:        MIT
URL:            https://github.com/pol-rivero/github-desktop-plus
Source0:        %{url}/releases/download/v%{version}/GitHubDesktopPlus-v%{version}-linux-x86_64.rpm

ExclusiveArch:  x86_64
BuildRequires: chrpath

%description
GitHub Desktop Plus (prebuilt binary). This package simply repackages the RPM for distribution via Copr.

%prep
# Nothing to do

%build
# Nothing to build

%install
mkdir -p %{buildroot}
rpm2cpio %{SOURCE0} | cpio -idmv -D %{buildroot}

# Remove broken internal git, force to use system git
rm -rf %{buildroot}/usr/lib/%{name}/resources/app/git

# Strip invalid RPATHs from embedded git binaries
for bin in %{buildroot}/usr/lib/%{name}/resources/app/git/libexec/git-core/git-*; do
    if file "$bin" | grep -q ELF && chrpath -l "$bin" | grep -q '/tmp/build'; then
        chrpath -d "$bin"
    fi
done

%files
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
/usr/lib/%{name}/**
/usr/share/doc/%{name}/copyright

%changelog
%autochangelog