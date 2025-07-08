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
BuildRequires: cmake alsa-lib-devel openssl-devel rust cargo
BuildRequires: gstreamer1-devel gstreamer1-plugins-base-devel libvpx-devel
BuildRequires: rust cargo gcc-c++ libvpx-devel pam-devel
BuildRequires: opus-devel libyuv-devel pkgconfig

ExclusiveArch: x86_64

%description
RuskDesk is a remote desktop software that allows you to access and control computers remotely.

%prep
# Clone the RustDesk source
git clone --recurse-submodules https://github.com/rustdesk/rustdesk.git rustdesk
cd rustdesk
git submodule update --init --recursive

# Download libsciter-gtk.so (optional runtime dependency)
mkdir -p target/debug
wget -O target/debug/libsciter-gtk.so https://raw.githubusercontent.com/c-smile/sciter-sdk/master/bin.lnx/x64/libsciter-gtk.so

# Set up Cargo config to vendor dependencies
mkdir -p .cargo
cat > .cargo/config.toml <<EOF
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF

# Step 1: Vendor dependencies (before patching)
cargo vendor vendor

# Step 2: Patch webm-sys to use system libvpx and allow RTTI
WEBM_RS=vendor/webm-sys/build.rs
if [ -f "$WEBM_RS" ]; then
  echo "⚙️ Patching $WEBM_RS"
  sed -i 's/build.flag_if_supported("-fno-exceptions");/\/\/ removed -fno-exceptions/' "$WEBM_RS"
  sed -i 's/build.flag_if_supported("-fno-rtti");/\/\/ removed -fno-rtti/' "$WEBM_RS"
  sed -i 's/^.*let use_pkg_config = .*;/let use_pkg_config = true; \/\/ force system libvpx/' "$WEBM_RS"
else
  echo "❌ $WEBM_RS not found"
  exit 1
fi

# Fix missing <cstdint> in mkvparser.cc
MKVPARSER=vendor/webm-sys/libwebm/mkvparser/mkvparser.cc
if grep -q 'common/webmids.h' "$MKVPARSER"; then
  echo "🔧 Patching mkvparser.cc to include <cstdint>"
  sed -i '/common\/webmids\.h/a #include <cstdint>' "$MKVPARSER"
else
  echo "❌ Could not patch mkvparser.cc - include line not found"
  exit 1
fi

# Step 3: Patch magnum-opus to use pkg-config for opus
MAGNUM_RS=vendor/magnum-opus/build.rs
MAGNUM_TOML=vendor/magnum-opus/Cargo.toml

if [ -f "$MAGNUM_RS" ]; then
  echo "⚙️  Patching $MAGNUM_RS to use pkg-config"
  sed -i 's/^\s*panic!.*VCPKG_ROOT.*/pkg_config::probe_library("opus").unwrap();/' "$MAGNUM_RS"
  grep -q '^extern crate pkg_config;' "$MAGNUM_RS" || sed -i '1i extern crate pkg_config;' "$MAGNUM_RS"
else
  echo "❌ $MAGNUM_RS not found"
  exit 1
fi

# Fix magnum-opus Cargo.toml to declare pkg-config as optional
if [ -f "$MAGNUM_TOML" ]; then
  echo "📦 Fixing $MAGNUM_TOML for optional pkg-config feature"

  # Clean up any prior bad definitions
  sed -i '/^\[build-dependencies\]/,/^\[.*\]/ {/pkg-config/d}' "$MAGNUM_TOML"
  sed -i '/pkg-config\s*=.*/d' "$MAGNUM_TOML"
  sed -i '/optional\s*=\s*true/d' "$MAGNUM_TOML"

  # Ensure [dependencies] exists
  grep -q '^\[dependencies\]' "$MAGNUM_TOML" || echo '[dependencies]' >> "$MAGNUM_TOML"
  grep -q '^pkg-config' "$MAGNUM_TOML" || echo 'pkg-config = { version = "0.3", optional = true }' >> "$MAGNUM_TOML"

  # Ensure [features] and linux-pkg-config exists
  grep -q '^\[features\]' "$MAGNUM_TOML" || echo '[features]' >> "$MAGNUM_TOML"
  grep -q '^linux-pkg-config' "$MAGNUM_TOML" || echo 'linux-pkg-config = ["pkg-config"]' >> "$MAGNUM_TOML"
else
  echo "❌ $MAGNUM_TOML not found"
  exit 1
fi

# Step 4: Patch Cargo.toml to override git dependencies
cat >> Cargo.toml <<EOF

[patch."https://github.com/rustdesk-org/rust-webm"]
webm-sys = { path = "vendor/webm-sys" }

[patch."https://github.com/rustdesk-org/magnum-opus"]
magnum-opus = { path = "vendor/magnum-opus" }
EOF

# Step 5: Move into top-level build root
cd ..
cp -a rustdesk/. ./
rm -rf rustdesk


%build
export CXXFLAGS="%{optflags} -fexceptions -frtti"
export RUSTFLAGS="-C link-arg=-Wl,-rpath=%{_libdir}"
export PKG_CONFIG_PATH="%{_libdir}/pkgconfig"
export PKG_CONFIG_ALLOW_CROSS=1

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
