Name:           github-desktop
Version:        3.5.0
Release:        1%{?dist}
Summary:        GitHub Desktop Plus

License:        MIT
URL:            https://github.com/pol-rivero/github-desktop-plus
Source0:        %{url}/releases/download/v%{version}/GitHubDesktopPlus-v%{version}-linux-x86_64.rpm

BuildArch:      noarch
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

# Strip invalid RPATHs
for bin in %{buildroot}/usr/lib/github-desktop/resources/app/git/libexec/git-core/git-*; do
    if chrpath -l "$bin" | grep -q '/tmp/build'; then
        chrpath -d "$bin"
    fi
done

%files
/usr/*

%changelog
%autochangelog