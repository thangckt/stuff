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

# Strip invalid RPATHs from all ELF binaries (shared objects and executables)
find %{buildroot} -type f \( -name '*.so' -o -perm -111 \) | while read -r bin; do
    if file "$bin" | grep -q ELF; then
        if chrpath -l "$bin" 2>/dev/null | grep -q '/workspace/'; then
            echo "Stripping RPATH from $bin"
            chrpath -d "$bin"
        fi
    fi
done

# (Optional) See files in the buildroot (for debug only — remove this in final version)
find %{buildroot}

%post
alternatives --install %{_bindir}/%{name} %{name} /opt/%{name}/%{name} 100

%postun
if [ -x %{_bindir}/%{name} ] && alternatives --display %{name} &>/dev/null; then
    alternatives --remove %{name} %{_bindir}/%{name}
fi

%files
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png

%changelog
%autochangelog