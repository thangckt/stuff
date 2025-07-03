Name:           rustdesk
Version:        1.4.0
Release:        1%{?dist}
Summary:        GitHub Desktop Plus

License:        GNU General Public License v3.0
URL:            https://github.com/rustdesk/rustdesk
Source0:        %{url}/releases/download/%{version}/%{name}-%{version}-0.x86_64.rpm


ExclusiveArch:  x86_64
BuildRequires: chrpath

Requires: libappindicator-gtk3

%description
RuskDesk (prebuilt binary). This package simply repackages the RPM for distribution via Copr.

%prep
# Nothing to do

%build
# Nothing to build

%install
mkdir -p %{buildroot}
rpm2cpio %{SOURCE0} | cpio -idmv -D %{buildroot}

# Strip invalid RPATHs from all ELF binaries (shared objects and executables)
find %{buildroot} -type f \( -name '*.so' -o -perm -111 \) | while read -r bin; do
    if file "$bin" | grep -q ELF; then
        if chrpath -l "$bin" 2>/dev/null | grep -q '/workspace/'; then
            echo "Stripping RPATH from $bin"
            chrpath -d "$bin"
        fi
    fi
done

# The .desktop file is not in `applications` directory (not found in applications menu)
mkdir -p %{buildroot}%{_datadir}/applications
cp %{buildroot}%{_datadir}/rustdesk/files/rustdesk.desktop %{buildroot}%{_datadir}/applications/rustdesk.desktop

# the executable file rustdesk is not in the PATH: /usr/bin (not in %{_bindir})
mkdir -p %{buildroot}%{_bindir}
ln -s %{_datadir}/rustdesk/rustdesk %{buildroot}%{_bindir}/rustdesk

%files
%{_bindir}/rustdesk
%{_datadir}/rustdesk/**
%{_datadir}/applications/rustdesk.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/icons/hicolor/*/apps/%{name}.svg

%changelog
%autochangelog