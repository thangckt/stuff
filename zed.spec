### ref: https://github.com/terrapkg/packages/blob/frawhide/anda/devs/zed/stable/zed.spec
### Note:
#  - simplify desktop file from the original: https://github.com/zed-industries/zed/blob/main/crates/zed/resources/zed.desktop.in

Name:           zed
Version:        0.198.5
Release:        1%{?dist}
Summary:        High-performance, multiplayer code editor

License:        AGPL-3.0-only AND Apache-2.0 AND GPL-3.0-or-later
URL:            https://zed.dev/
Source0:        https://github.com/zed-industries/zed/archive/refs/tags/v%{version}.tar.gz

# Vendored dependencies tarball (created with `cargo vendor`)
# This avoids network access in Copr builds
Source1:        zed-%{version}-vendor.tar.zst

BuildRequires:  cargo-rpm-macros >= 24
BuildRequires:  gcc, gcc-c++, clang, cmake, git
BuildRequires:  alsa-lib-devel, fontconfig-devel, wayland-devel
BuildRequires:  libxkbcommon-x11-devel, openssl-devel
BuildRequires:  libzstd-devel, vulkan-loader-devel, libcurl-devel
BuildRequires:  expat-devel, libxcb-devel, libX11-devel, libXi-devel

Conflicts:      zed-nightly
Conflicts:      zed-preview

%description
Code at the speed of thought — Zed is a high-performance, multiplayer code editor from the creators of Atom and Tree-sitter.

%prep
%autosetup -n zed-%{version} -p1
# Unpack vendored Rust crates
tar --strip-components=1 -xf %{SOURCE1}

### Or replace all pre section by clone Zed with submodules
# git clone --recurse-submodules https://github.com/zed-industries/zed.git zed
# cd zed
# git checkout v%{version}
# git submodule update --init --recursive
# cd ..
# cp -a zed/. ./
# rm -rf zed

%build
export CARGO_HOME=$(pwd)/.cargo
export RUSTFLAGS="%{build_ldflags} %{?__global_ldflags}"
cargo build --release --offline --package zed

%install
install -Dpm755 target/release/zed %{buildroot}%{_bindir}/zed

## Desktop file
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/zed.desktop <<'EOF'
[Desktop Entry]
Name=Zed Editor
GenericName=Text Editor
Exec=zed %U
Icon=zed
Type=Application
StartupNotify=true
Categories=Utility;TextEditor;Development;IDE;
MimeType=text/plain;application/x-zerosize;x-scheme-handler/zed;
Actions=NewWorkspace;
Keywords=zed;

[Desktop Action NewWorkspace]
Name=Open a new workspace
Exec=zed --new %U
EOF

## Icon
install -Dpm644 crates/zed/resources/app-icon.png \
    %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/zed.png

%files
%{_bindir}/zed
%{_datadir}/applications/zed.desktop
%{_datadir}/icons/hicolor/128x128/apps/zed.png
%license LICENSE-AGPL LICENSE-APACHE LICENSE-GPL
%doc README.md

%changelog
%autochangelog
