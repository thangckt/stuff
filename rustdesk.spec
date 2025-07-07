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
BuildRequires: gstreamer1-devel gstreamer1-plugins-base-devel

Requires:      hicolor-icon-theme

%description
RuskDesk is a remote desktop software that allows you to access and control computers remotely.

%prep
# Clone the repository with submodules
git clone --recurse-submodules https://github.com/rustdesk/rustdesk.git rustdesk
cd rustdesk
# git checkout %{version}
git submodule update --init --recursive

# Download libsciter runtime
mkdir -p target/debug
wget -O target/debug/libsciter-gtk.so https://raw.githubusercontent.com/c-smile/sciter-sdk/master/bin.lnx/x64/libsciter-gtk.so

# Patch: Disable -fno-exceptions in webm-sys build.rs
WEBM_BUILD_RS="vendor/webm-sys/build.rs"
if grep -q '\-fno-exceptions' "$WEBM_BUILD_RS"; then
    echo "Patching $WEBM_BUILD_RS to remove -fno-exceptions"
    sed -i 's/.*-fno-exceptions.*/\/\/ removed -fno-exceptions for RPM build/' "$WEBM_BUILD_RS"
fi

# Move source to expected build directory root
cd ..
cp -a rustdesk/. ./
rm -rf rustdesk

%build
export RUSTFLAGS="-C link-arg=-Wl,-rpath=%{_libdir}"
cargo build --release

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
