Name:           zotero
Version:        7.0.19
Release:        1%{?dist}
Summary:        Zotero – Reference Manager (GUI, Linux)

License:        AGPL-3.0-only
URL:            https://github.com/zotero/zotero
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz
Source1:        https://github.com/zotero/zotero-build/archive/refs/heads/master.tar.gz

BuildRequires:  git
BuildRequires:  nodejs
BuildRequires:  npm
BuildRequires:  yarn
BuildRequires:  gtk3-devel
BuildRequires:  libXt-devel
BuildRequires:  libX11-devel
BuildRequires:  dbus-glib-devel
BuildRequires:  gcc-c++
BuildRequires:  python3

Requires:       gtk3
Requires:       libXt
Requires:       libX11
Requires:       dbus-glib

%description
Zotero is a powerful reference manager that can be used to manage bibliographic data and related research materials.

%prep
%autosetup -p1 -n zotero-%{version}
tar xzf %{SOURCES}/master.tar.gz -C builddir
# Now builddir contains zotero-build master

%build
pushd builddir/zotero-build-master
npm install
# example build script
npm run dist-linux
popd

%install
# adjust paths to actual output location
install -Dm0755 builddir/zotero-build-master/output/zotero %{buildroot}%{_bindir}/zotero
install -Dm0644 builddir/zotero-build-master/output/zotero.desktop %{buildroot}%{_datadir}/applications/zotero.desktop
cp -a builddir/zotero-build-master/output/chrome builddir/zotero-build-master/output/resource %{buildroot}%{_datadir}/zotero/

%files
%license COPYING
%{_bindir}/zotero
%{_datadir}/applications/zotero.desktop
%{_datadir}/zotero/

%changelog