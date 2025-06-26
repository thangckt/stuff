Name:           zotero
Version:        7.0.19
Release:        1%{?dist}
Summary:        Zotero – Reference Manager (GUI, Linux)

License:        AGPL-3.0-only
URL:            https://github.com/zotero/zotero
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  git
BuildRequires:  npm
BuildRequires:  nodejs
BuildRequires:  python3
BuildRequires:  libgtk-3.0-devel
BuildRequires:  libdbus-glib-devel
BuildRequires:  libXt-devel
BuildRequires:  libx11-devel
BuildRequires:  gcc-c++
BuildRequires:  unzip

Requires:       gtk3
Requires:       libdbus-glib
Requires:       libXt
Requires:       libX11

%description
Zotero is a free, open-source tool to help you collect, organize, cite, and share research sources. This package builds the Linux GUI application.

%prep
%autosetup

%build
# Prepare fetch and build script from upstream
cd build
cp ../build.sh .
cp ../config.sh .
chmod +x build.sh
./build.sh -l linux-x86_64

%install
cd build/Zotero_linux-x86_64
install -d %{buildroot}%{_bindir}
install -m 0755 zotero %{buildroot}%{_bindir}
install -d %{buildroot}%{_datadir}/applications
install -m 0644 zotero.desktop %{buildroot}%{_datadir}/applications

# Install support files
install -d %{buildroot}%{_prefix}/share/zotero
cp -r chrome resource %{buildroot}%{_prefix}/share/zotero/

%files
%license COPYING
%{_bindir}/zotero
%{_datadir}/applications/zotero.desktop
%{_prefix}/share/zotero/

%changelog