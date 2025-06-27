Name:           zotero
Version:        7.0.19
Release:        1%{?dist}
Summary:        Zotero – Reference Manager (GUI, Linux)

License:        AGPL-3.0-only
URL:            https://github.com/zotero/zotero
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

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
BuildRequires:  mozjs-devel  # if available for JavaScript engine
BuildRequires:  desktop-file-utils

Requires:       hicolor-icon-theme
Requires:       gtk3
Requires:       libXt
Requires:       libX11
Requires:       dbus-glib

%description
Zotero is a powerful reference manager that helps you collect, organize, cite, and share research publications. This package builds Zotero from source using Mozilla’s build system (mach).

%prep
%autosetup -n zotero-%{version}

# Ensure third-party components and submodules are fetched
git submodule update --init --recursive

%build
# Set environment if needed
export MOZCONFIG=$(pwd)/build/linux64-config

# Run Zotero's build system via mach
./mach build

# After running `./mach build`, the browser is packaged into a dist directory
# We're not installing system-wide, just packaging contents under dist/

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/zotero
cp -a dist/linux64-unpacked/* %{buildroot}/opt/zotero/

# Create a symlink
mkdir -p %{buildroot}%{_bindir}
ln -s /opt/zotero/zotero %{buildroot}%{_bindir}/zotero

# Desktop integration
mkdir -p %{buildroot}%{_datadir}/applications
install -Dm644 %{buildroot}/opt/zotero/zotero.desktop %{buildroot}%{_datadir}/applications/zotero.desktop

# Icons
for icon in %{buildroot}/opt/zotero/chrome/icons/default/default*.png; do
    size=$(basename "$icon" | sed -E 's/default([0-9]+)\.png/\1/')
    mkdir -p %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps
    cp -a "$icon" %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/zotero.png
done

%files
%license LICENSE.txt
%{_bindir}/zotero
/opt/zotero
%{_datadir}/applications/zotero.desktop
%{_datadir}/icons/hicolor/*/apps/zotero.png

%post
update-desktop-database &> /dev/null || :

%postun
update-desktop-database &> /dev/null || :

%changelog
%autochangelog