### ref: https://github.com/terrapkg/packages/blob/frawhide/anda/devs/zed/stable/zed.spec

Name:           zed
Version:        0.194.3
Release:        1%{?dist}
Summary:        Zed is a high-performance, multiplayer code editor

License:        AGPL-3.0-only AND Apache-2.0 AND GPL-3.0-or-later
URL:            https://zed.dev/
Source0:        https://github.com/zed-industries/zed/archive/refs/tags/v%{version}.tar.gz

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
# Clone the Zed source with submodules at the specified version
git clone --recurse-submodules https://github.com/zed-industries/zed.git zed
cd zed
git checkout v%{version}
git submodule update --init --recursive
cd ..
# Move Zed source to expected RPM build root
cp -a zed/. ./
rm -rf zed

# Clone the 'notify' dependency used by Zed at pinned revision
git clone https://github.com/zed-industries/notify.git notify
cd notify
git checkout bbb9ea5ae52b253e095737847e367c30653a2e96
cd ..

# Replace existing notify entry in Cargo.toml with local path pointing to the notify package within the workspace
sed -i '/^\[patch.crates-io\]/,/^\[/ { /^notify = { git.*notify\.git.*rev.*bbb9ea5ae52b253e095737847e367c30653a2e96.*}/ s/.*/notify = { path = "notify\/notify" }/ }' Cargo.toml

# Generate desktop and metainfo files using envsubst
export APP_ID=dev.zed.Zed
envsubst < crates/zed/resources/zed.desktop.in > %{APP_ID}.desktop
envsubst < crates/zed/resources/flatpak/zed.metainfo.xml.in > %{APP_ID}.metainfo.xml

%build
%cargo_build -- --package zed --package cli
script/generate-licenses

%install
install -Dm755 target/release/zed %{buildroot}%{_libexecdir}/zed-editor
install -Dm755 target/release/cli %{buildroot}%{_bindir}/zed

install -Dm644 %{APP_ID}.desktop %{buildroot}%{_datadir}/applications/%{APP_ID}.desktop
install -Dm644 crates/zed/resources/app-icon.png %{buildroot}%{_datadir}/pixmaps/%{APP_ID}.png
install -Dm644 %{APP_ID}.metainfo.xml %{buildroot}%{_metainfodir}/%{APP_ID}.metainfo.xml

%files
%license LICENSE-AGPL LICENSE-APACHE LICENSE-GPL
%doc README.md
%{_libexecdir}/zed-editor
%{_bindir}/zed
%{_datadir}/applications/dev.zed.Zed.desktop
%{_datadir}/pixmaps/dev.zed.Zed.png
%{_metainfodir}/dev.zed.Zed.metainfo.xml

%changelog
%autochangelog
