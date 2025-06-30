### This code with the help by Claude and ChatGPT

Name:           github-desktop-plus
Version:        3.5.0
Release:        1%{?dist}
Summary:        GitHub Desktop Plus

License:        MIT
URL:            https://github.com/pol-rivero/github-desktop-plus
Source0:        %{url}/releases/download/v%{version}/GitHubDesktopPlus-v%{version}-linux-x86_64.rpm

BuildArch:      noarch
ExclusiveArch:  x86_64

%description
GitHub Desktop Plus (prebuilt binary). This package simply repackages the RPM for distribution via Copr.

%prep
# Nothing to do

%build
# Nothing to build

%install
mkdir -p %{buildroot}
rpm2cpio %{SOURCE0} | cpio -idmv -D %{buildroot}

%files
/usr/*

%changelog
%autochangelog