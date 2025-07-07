### REF: https://rustdesk.com/docs/en/dev/build/linux/

Name:           rustdesk
Version:        1.4.0
Release:        1%{?dist}
Summary:        Remote desktop software for control and file transfer

License:        GPL-3.0-only
URL:            https://github.com/rustdesk/rustdesk
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz


BuildRequires: gcc-c++ git curl wget nasm yasm gcc gtk3-devel clang
BuildRequires: libxcb-devel libxdo-devel libXfixes-devel pulseaudio-libs-devel
BuildRequires: cmake alsa-lib-devel openssl-devel pkgconfig rust cargo
BuildRequires: gstreamer1-devel gstreamer1-plugins-base-devel libvpx-devel
BuildRequires: rust cargo gcc-c++ pkgconfig libvpx-devel pam-devel
BuildRequires: opus-devel libyuv-devel

ExclusiveArch: x86_64

%description
RuskDesk is a remote desktop software that allows you to access and control computers remotely.

%prep
git clone --recurse-submodules https://github.com/rustdesk/rustdesk.git rustdesk
cd rustdesk
git submodule update --init --recursive

# Download libsciter
mkdir -p target/debug
wget -O target/debug/libsciter-gtk.so https://raw.githubusercontent.com/c-smile/sciter-sdk/master/bin.lnx/x64/libsciter-gtk.so

# Generate .cargo config for vendoring
mkdir -p .cargo
cat > .cargo/config.toml <<EOF
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF

# Vendor dependencies
cargo vendor vendor

# Patch webm-sys in vendor
WEBM_RS=vendor/webm-sys/build.rs
if [ -f "$WEBM_RS" ]; then
  echo "⚙️ Patching $WEBM_RS"
  sed -i 's/build.flag_if_supported("-fno-exceptions");/\/\/ removed -fno-exceptions/' "$WEBM_RS"
  sed -i 's/build.flag_if_supported("-fno-rtti");/\/\/ removed -fno-rtti/' "$WEBM_RS"
  sed -i 's/^.*let use_pkg_config = .*;/let use_pkg_config = true; \/\/ force system libvpx/' "$WEBM_RS"
else
  echo "❌ $WEBM_RS not found"
  find vendor -name build.rs | grep webm-sys || true
  exit 1
fi

# Patch libwebm/mkvparser/mkvparser.cc to include <cstdint>
MKVPARSER=vendor/webm-sys/libwebm/mkvparser/mkvparser.cc
if grep -q 'common/webmids.h' "$MKVPARSER"; then
  echo "🔧 Patching mkvparser.cc to include <cstdint>"
  sed -i '/common\/webmids\.h/a #include <cstdint>' "$MKVPARSER"
else
  echo "❌ Could not patch mkvparser.cc - include line not found"
  exit 1
fi

# Patch magnum-opus build.rs to force pkg-config
MAGNUM_RS=vendor/magnum-opus/build.rs
if [ -f "$MAGNUM_RS" ]; then
  echo "⚙️  Patching $MAGNUM_RS to force pkg-config"
  sed -i 's/^\s*panic!.*VCPKG_ROOT.*/pkg_config::probe_library("opus").unwrap();/' "$MAGNUM_RS"
else
  echo "❌ $MAGNUM_RS not found"
  exit 1
fi

# Force local override even for Git-based dependency
cat >> Cargo.toml <<EOF

[patch."https://github.com/rustdesk-org/rust-webm"]
webm-sys = { path = "vendor/webm-sys" }
EOF

# Move to RPM build root
cd ..
cp -a rustdesk/. ./
rm -rf rustdesk

%build
export CXXFLAGS="%{optflags} -fexceptions -frtti"
export RUSTFLAGS="-C link-arg=-Wl,-rpath=%{_libdir}"
export PKG_CONFIG_PATH="%{_libdir}/pkgconfig"
export PKG_CONFIG_ALLOW_CROSS=1

# Build with vendored sources and patched webm-sys
cargo build --release --offline

%install
install -Dm755 target/release/rustdesk %{buildroot}%{_bindir}/rustdesk

# Icon
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/512x512/apps
cp -v images/rustdesk.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
cp -v images/rustdesk.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/%{name}.png

# Optional systemd service (if provided)
if [ -f files/rustdesk.service ]; then
    mkdir -p %{buildroot}%{_unitdir}
    cp -v files/rustdesk.service %{buildroot}%{_unitdir}/
fi

%files
%{_bindir}/rustdesk
%{_datadir}/applications/rustdesk.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.*
%{_unitdir}/rustdesk.service

%changelog
%autochangelog
