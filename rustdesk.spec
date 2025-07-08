### REF: https://rustdesk.com/docs/en/dev/build/linux/

Name:           rustdesk
Version:        1.4.0
Release:        1%{?dist}
Summary:        Remote desktop software for control and file transfer

License:        GPL-3.0-only
URL:            https://github.com/rustdesk/rustdesk
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  rust cargo
BuildRequires:  cmake
BuildRequires:  pkgconfig
BuildRequires:  gtk3-devel
BuildRequires:  libxcb-devel
BuildRequires:  libxdo-devel
BuildRequires:  libXfixes-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  alsa-lib-devel
BuildRequires:  openssl-devel
BuildRequires:  gstreamer1-devel
BuildRequires:  gstreamer1-plugins-base-devel
BuildRequires:  libvpx-devel
BuildRequires:  pam-devel
BuildRequires:  opus-devel
BuildRequires:  libyuv-devel
BuildRequires:  clang

ExclusiveArch:  x86_64

%description
RustDesk is a remote desktop software that allows you to access and control computers remotely.

%prep
%autosetup -n %{name}-%{version}

# Download libsciter-gtk.so (runtime dependency)
mkdir -p target/debug
curl -L -o target/debug/libsciter-gtk.so https://raw.githubusercontent.com/c-smile/sciter-sdk/master/bin.lnx/x64/libsciter-gtk.so

%build
export CXXFLAGS="%{optflags} -fexceptions -frtti"
export RUSTFLAGS="-C link-arg=-Wl,-rpath=%{_libdir}"

# Use system libraries where possible
export PKG_CONFIG_PATH="%{_libdir}/pkgconfig"
export PKG_CONFIG_ALLOW_CROSS=1

cargo build --release

%install
install -Dm755 target/release/rustdesk %{buildroot}%{_bindir}/rustdesk

# Desktop file
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/rustdesk.desktop << EOF
[Desktop Entry]
Name=RustDesk
Comment=Remote desktop software
Exec=rustdesk
Icon=rustdesk
Type=Application
Categories=Network;RemoteAccess;
Terminal=false
EOF

# Icons
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/512x512/apps
install -Dm644 res/rustdesk.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/rustdesk.svg
install -Dm644 res/rustdesk.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/rustdesk.png

%files
%license LICENSE
%doc README.md
%{_bindir}/rustdesk
%{_datadir}/applications/rustdesk.desktop
%{_datadir}/icons/hicolor/*/apps/rustdesk.*

%changelog
%autochangelog
