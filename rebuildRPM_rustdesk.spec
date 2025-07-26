Name:           rustdesk
Version:        1.4.0
Release:        1%{?dist}
Summary:        Remote desktop software

License:        GNU General Public License v3.0
URL:            https://github.com/rustdesk/rustdesk
Source0:        %{url}/releases/download/%{version}/%{name}-%{version}-0.x86_64.rpm


ExclusiveArch:  x86_64
BuildRequires: chrpath

Requires: libappindicator-gtk3 xdg-desktop-portal

%description
RuskDesk (prebuilt binary). This package simply repackages the RPM for distribution via Copr.

%prep
# Nothing to do

%build
# Nothing to do

%install
mkdir -p %{buildroot}
rpm2cpio %{SOURCE0} | cpio -idmv -D %{buildroot}

# Strip invalid RPATHs from all ELF binaries (shared objects and executables)
find %{buildroot} -type f \( -name '*.so' -o -perm -111 \) -exec sh -c '
    for bin; do
        if file "$bin" | grep -q ELF && chrpath -l "$bin" 2>/dev/null | grep -q "/workspace/"; then
            echo "Stripping RPATH from $bin"
            chrpath -d "$bin"
        fi
    done
' sh {} +

# Strip debug symbols to reduce binary size
find %{buildroot} -type f -name '*.so' -exec strip --strip-unneeded {} +
find %{buildroot} -type f -perm -111 -exec strip --strip-unneeded {} +

# The .desktop file is not in `applications` directory (not found in applications menu)
mkdir -p %{buildroot}%{_datadir}/applications
install -m 644 %{buildroot}%{_datadir}/rustdesk/files/rustdesk.desktop %{buildroot}%{_datadir}/applications/rustdesk.desktop

# The executable file rustdesk is not in the PATH, e.g., /usr/bin (not in %{_bindir})
mkdir -p %{buildroot}%{_bindir}
ln -s %{_datadir}/rustdesk/rustdesk %{buildroot}%{_bindir}/rustdesk

# Move the service file to the correct systemd location
mkdir -p %{buildroot}/usr/lib/systemd/system
install -m 644 %{buildroot}%{_datadir}/rustdesk/files/rustdesk.service %{buildroot}/usr/lib/systemd/system/rustdesk.service

%files
%{_bindir}/rustdesk
%{_datadir}/rustdesk/**
%{_datadir}/applications/rustdesk.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/icons/hicolor/*/apps/%{name}.svg
/usr/lib/systemd/system/rustdesk.service

%changelog
%autochangelog
