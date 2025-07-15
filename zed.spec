### ref: https://github.com/terrapkg/packages/blob/frawhide/anda/devs/zed/stable/zed.spec

Name:           zed
Version:        0.194.3
Release:        1%{?dist}
Summary:        Zed is a high-performance, multiplayer code editor

License:        AGPL-3.0-only AND Apache-2.0 AND GPL-3.0-or-later
URL:            https://zed.dev/
Source0:        https://github.com/zed-industries/zed/archive/refs/tags/v%{version}.tar.gz

BuildRequires:  cargo-rpm-macros >= 24
BuildRequires:  gcc, gcc-c++, clang, cmake, mold
BuildRequires:  alsa-lib-devel, fontconfig-devel, wayland-devel
BuildRequires:  libxkbcommon-x11-devel, openssl-devel
BuildRequires:  libzstd-devel, vulkan-loader, libcurl-devel
BuildRequires:  gettext-envsubst

Conflicts:      zed-nightly
Conflicts:      zed-preview

%description
Code at the speed of thought — Zed is a high-performance, multiplayer code editor from the creators of Atom and Tree-sitter.

%prep
%autosetup -n zed-%{version}
%cargo_prep

# Set up desktop integration
export APP_ID=dev.zed.Zed
envsubst < crates/zed/resources/zed.desktop.in > %{APP_ID}.desktop
envsubst < crates/zed/resources/flatpak/zed.metainfo.xml.in > %{APP_ID}.metainfo.xml

%build
echo "stable" > crates/zed/RELEASE_CHANNEL
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
