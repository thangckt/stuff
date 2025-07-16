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
# Clone Zed with submodules
git clone --recurse-submodules https://github.com/zed-industries/zed.git zed
cd zed
git checkout v%{version}
git submodule update --init --recursive
cd ..
cp -a zed/. ./
rm -rf zed

# Clone the notify workspace repo
git clone https://github.com/zed-industries/notify.git notify
cd notify
git checkout bbb9ea5ae52b253e095737847e367c30653a2e96

# Patch in a minimal [workspace.package] rust-version
# This is required so the actual notify crate can inherit it
echo -e '\n[workspace.package]\nrust-version = "1.70"' >> Cargo.toml
cd ..

# Remove existing notify Git override
awk '
  BEGIN { inside_patch = 0 }
  /^\[patch\.crates-io\]/ { inside_patch = 1; print; next }
  /^\[/ && inside_patch { inside_patch = 0 }
  inside_patch && /^\s*notify\s*=/ { next }
  { print }
' Cargo.toml > Cargo.toml.new && mv Cargo.toml.new Cargo.toml

# Add local path override
if grep -q '^\[patch.crates-io\]' Cargo.toml; then
  sed -i '/^\[patch.crates-io\]/a notify = { path = "notify/notify" }' Cargo.toml
else
  echo -e '\n[patch.crates-io]\nnotify = { path = "notify/notify" }' >> Cargo.toml
fi

# Desktop files
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
