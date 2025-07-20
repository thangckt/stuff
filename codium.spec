### REF: https://gitlab.com/athenaos/packages/applications/vscodium/-/blob/main/rpm/vscodium.spec?ref_type=heads

Name:           codium
Version:        1.102.14746
Release:        5%{?dist}
Summary:        Free/Libre Open Source Software Binaries of VSCode

License:        MIT
URL:            https://github.com/VSCodium/vscodium
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

# Set VSCODE_ARCH based on the system architecture
%global vscode_arch x64
%ifarch aarch64
%global vscode_arch arm64
%endif

BuildRequires: gcc gcc-c++ make pkgconf
BuildRequires: git jq fakeroot ripgrep
BuildRequires: python3 nodejs-npm rustup
BuildRequires: libX11-devel libxkbfile-devel libsecret-devel krb5-devel

%description
VSCodium is a community-driven, freely-licensed binary distribution of Microsoft’s VS Code.
This package builds it from the official source using a reproducible process.

%prep
%autosetup -n vscodium-%{version}

%build
# Environment setup
export PATH=%{_bindir}:$PATH
export NODE_OPTIONS=--openssl-legacy-provider

export VSCODE_ARCH=%{vscode_arch}
export VSCODE_QUALITY="stable"
export RELEASE_VERSION="%{version}"
export SHOULD_BUILD="yes"
export SHOULD_BUILD_REH="no"
export CI_BUILD="no"
export OS_NAME="linux"
export DISABLE_UPDATE="yes"

# Rust setup
rustup-init -y
. "$HOME/.cargo/env"

# Build
sed -i "s#. version.sh#. ./version.sh#g" build.sh
sed -i "s#. prepare_vscode.sh#. ./prepare_vscode.sh#g" build.sh
. ./get_repo.sh
. ./build.sh

%install
mkdir -p %{buildroot}/usr/share/vscodium
cp -r VSCode-linux-%{vscode_arch}/* %{buildroot}/usr/share/vscodium/

# Replace statically included binary with system copy. It allows the usage of Fedora ripgrep binary that includes build-id
ln -sf /usr/bin/rg %{buildroot}/usr/share/vscodium/resources/app/node_modules/@vscode/ripgrep/bin/rg

# Symlink binary
mkdir -p %{buildroot}%{_bindir}
ln -s /usr/share/vscodium/bin/codium %{buildroot}%{_bindir}/codium

# Desktop entry
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop << 'EOF'
[Desktop Entry]
Name=VSCodium
GenericName=Text Editor
Exec=/usr/bin/codium %F
Icon=%{name}
Type=Application
Terminal=false
StartupNotify=false
StartupWMClass=VSCodium
Categories=Utility;Development;IDE;
MimeType=text/plain;inode/directory;application/x-code-workspace;
Actions=new-empty-window;
Keywords=vscode;

[Desktop Action new-empty-window]
Name=New Empty Window
Exec=/usr/bin/codium --new-window %F
Icon=%{name}
EOF

# Icon
install -D -m644 VSCode-linux-%{vscode_arch}/resources/app/resources/linux/code.png \
  %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{name}.png

%files
%license LICENSE
%doc README.md
%{_bindir}/codium
%{_datadir}/vscodium
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/128x128/apps/%{name}.png

%changelog
%autochangelog
