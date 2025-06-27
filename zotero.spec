### REF: https://www.zotero.org/support/dev/client_coding/building_the_desktop_app

Name:           zotero
Version:        7.0.19
Release:        1%{?dist}
Summary:        Zotero – Reference Manager (GUI, Linux)

License:        AGPL-3.0-only
URL:            https://github.com/zotero/zotero
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz


%ifarch x86_64
BuildArch: x86_64
ExclusiveArch: x86_64
%else
%error Zotero only builds on x86_64. This build arch is %{_arch}
%endif

BuildRequires:  git
BuildRequires:  gtk3-devel
BuildRequires:  libXt-devel
BuildRequires:  libX11-devel
BuildRequires:  dbus-glib-devel
BuildRequires:  gcc-c++
BuildRequires:  python3
BuildRequires:  nodejs
BuildRequires:  rust
BuildRequires:  cargo
BuildRequires:  unzip
BuildRequires:  zip
BuildRequires:  clang  # for some parts of Firefox build
BuildRequires:  desktop-file-utils

Requires:       gtk3
Requires:       libXt
Requires:       libX11
Requires:       dbus-glib
Requires:       hicolor-icon-theme

%description
Zotero is a free, easy-to-use tool to help you collect, organize, cite, and share research. This package builds the Zotero client from source using Mozilla's `mach` build system.

%prep
%autosetup -n zotero-%{version}

# Ensure third-party components and submodules are fetched
git submodule update --init --recursive

%build
# Set environment for mach
export MACH_USE_SYSTEM_PYTHON=1
export MOZCONFIG=$(pwd)/build/linux64-config

# Build the application
./mach build

# After running `./mach build`, the browser is packaged into a dist directory
# We're not installing system-wide, just packaging contents under dist/

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/zotero
cp -a dist/linux64-unpacked/* %{buildroot}/opt/zotero/

# Create symlink to binary
install -d %{buildroot}%{_bindir}
ln -s /opt/zotero/zotero %{buildroot}%{_bindir}/zotero

# Desktop file
install -d %{buildroot}%{_datadir}/applications
install -m 644 build/linux64/zotero.desktop %{buildroot}%{_datadir}/applications/zotero.desktop || true

# Icon handling
for icon in %{buildroot}/opt/zotero/chrome/icons/default/default*.png; do
    size=$(basename "$icon" | sed -E 's/default([0-9]+)\.png/\1/')
    install -d %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps
    cp -a "$icon" %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/zotero.png
done

%files
%license LICENSE.txt
%{_bindir}/zotero
/opt/zotero
%{_datadir}/applications/zotero.desktop
%{_datadir}/icons/hicolor/*/apps/zotero.png

%post
update-desktop-database &>/dev/null || :

%postun
update-desktop-database &>/dev/null || :

%changelog
%autochangelog
