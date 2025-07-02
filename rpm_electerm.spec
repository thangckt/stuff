Name:           electerm
Version:        1.100.8
Release:        1%{?dist}
Summary:        GitHub Desktop Plus

License:        GNU General Public License v3.0
URL:            https://github.com/electerm/electerm
Source0:        %{url}/releases/download/v%{version}/electerm-%{version}-linux-x86_64.rpm


ExclusiveArch:  x86_64
BuildRequires: chrpath

%description
RuskDesk (prebuilt binary). This package simply repackages the RPM for distribution via Copr.

%prep
# Nothing to do

%build
# Nothing to build

%install
mkdir -p %{buildroot}
rpm2cpio %{SOURCE0} | cpio -idmv -D %{buildroot}

# Strip invalid RPATHs from embedded git binaries
for bin in %{buildroot}/usr/lib/%{name}/resources/app/git/libexec/git-core/git-*; do
    if file "$bin" | grep -q ELF && chrpath -l "$bin" | grep -q '/tmp/build'; then
        chrpath -d "$bin"
    fi
done

# (Optional) See files in the buildroot (for debug only — remove this in final version)
#find %{buildroot}

%post
alternatives --install %{_bindir}/%{name} %{name} /opt/%{name}/%{name} 100

%postun
if [ -x %{_bindir}/%{name} ] && alternatives --display %{name} &>/dev/null; then
    alternatives --remove %{name} %{_bindir}/%{name}
fi

%files
%dir /opt/electerm
/opt/electerm/*
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
/usr/lib/.build-id/*

%changelog
%autochangelog