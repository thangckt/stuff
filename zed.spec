### ref: https://github.com/terrapkg/packages/blob/frawhide/anda/devs/zed/stable/zed.spec

Name:           zed
Version:        0.196.6
Release:        1%{?dist}
Summary:        Zed is a high-performance, multiplayer code editor

License:        AGPL-3.0-only AND Apache-2.0 AND GPL-3.0-or-later
URL:            https://zed.dev/
#Source0:       https://github.com/zed-industries/zed/archive/refs/tags/v%{version}.tar.gz

BuildRequires:  cargo-rpm-macros >= 24
BuildRequires:  gcc, gcc-c++, clang, cmake, mold, git
BuildRequires:  alsa-lib-devel, fontconfig-devel, wayland-devel
BuildRequires:  libxkbcommon-x11-devel, openssl-devel
BuildRequires:  libzstd-devel, vulkan-loader, libcurl-devel
BuildRequires:  gettext-envsubst

Conflicts:      zed-nightly
Conflicts:      zed-preview

%description
Code at the speed of thought — Zed is a high-performance, multiplayer code editor from the creators of Atom and Tree-sitter.

%prep
# Clone Zed with submodules
git clone --recurse-submodules https://github.com/zed-industries/zed.git zed
cd zed
git checkout v%{version}
git submodule update --init --recursive
cd ..
cp -a zed/. ./
rm -rf zed

# Desktop files
export APP_ID=zed
export APP_NAME="Zed Editor"
export APP_CLI="zed"
export APP_ICON="zed"
export APP_ARGS="%U"
export DO_STARTUP_NOTIFY=true

# Generate desktop/metainfo files
envsubst < crates/zed/resources/zed.desktop.in > zed.desktop
envsubst < crates/zed/resources/flatpak/zed.metainfo.xml.in > zed.metainfo.xml

# Append StartupWMClass to ensure KDE task manager shows icon
grep -q '^StartupWMClass=' zed.desktop || sed -i '/^\[Desktop Action /i StartupWMClass=dev.zed.Zed' zed.desktop

%build
export CARGO_HOME=.cargo
cargo build -j%{_smp_build_ncpus} --release --package zed --package cli
script/generate-licenses

%install
install -Dm755 target/release/zed %{buildroot}%{_libexecdir}/zed-editor
install -Dm755 target/release/cli %{buildroot}%{_bindir}/zed

install -Dm644 zed.desktop %{buildroot}%{_datadir}/applications/zed.desktop
install -Dm644 crates/zed/resources/app-icon.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/zed.png
install -Dm644 zed.metainfo.xml %{buildroot}%{_metainfodir}/zed.metainfo.xml

%files
%license LICENSE-AGPL LICENSE-APACHE LICENSE-GPL
%doc README.md
%{_libexecdir}/zed-editor
%{_bindir}/zed
%{_datadir}/applications/zed.desktop
%{_datadir}/icons/hicolor/128x128/apps/zed.png
%{_metainfodir}/zed.metainfo.xml

%changelog
%autochangelog
