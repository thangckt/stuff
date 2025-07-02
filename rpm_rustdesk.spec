Name:           rustdesk
Version:        1.4.0
Release:        1%{?dist}
Summary:        GitHub Desktop Plus

License:        GNU General Public License v3.0
URL:            https://github.com/rustdesk/rustdesk
Source0:        %{url}/releases/download/%{version}/%{name}-%{version}-0.x86_64.rpm


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

# See files in the buildroot (to know what to put in files section)
find %{buildroot}

%files
%license /opt/rustdesk/LICENSE.electron.txt
/opt/rustdesk
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png

%changelog
%autochangelog