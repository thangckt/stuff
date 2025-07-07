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
BuildRequires: rust cargo gcc-c++ pkgconfig libvpx-devel

Requires:      hicolor-icon-theme

ExclusiveArch:  x86_64

%description
RuskDesk is a remote desktop software that allows you to access and control computers remotely.

%prep
# Clone the repository with submodules
git clone --recurse-submodules https://github.com/rustdesk/rustdesk.git rustdesk
cd rustdesk
git submodule update --init --recursive

# Download libsciter runtime
mkdir -p target/debug
wget -O target/debug/libsciter-gtk.so https://raw.githubusercontent.com/c-smile/sciter-sdk/master/bin.lnx/x64/libsciter-gtk.so

# Vendor dependencies locally
cargo vendor vendor

# Patch vendored webm-sys
sed -i 's/build.flag_if_supported("-fno-exceptions");/\/\/ removed -fno-exceptions/' vendor/webm-sys/build.rs
sed -i 's/build.flag_if_supported("-fno-rtti");/\/\/ removed -fno-rtti/' vendor/webm-sys/build.rs

# Move to build root
cd ..
cp -a rustdesk/. ./
rm -rf rustdesk

%build
export CXXFLAGS="%{optflags} -fexceptions -frtti"
export RUSTFLAGS="-C link-arg=-Wl,-rpath=%{_libdir}"

# Configure cargo to use vendor dir
mkdir .cargo
cat > .cargo/config <<EOF
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF

# Now build with vendored sources
cargo build --release --frozen

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
