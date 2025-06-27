Name:           zotero
Version:        7.0.19
Release:        1%{?dist}
Summary:        Zotero – Reference Manager (GUI, Linux)

License:        AGPL-3.0-only
URL:            https://github.com/zotero/zotero
Source0:        https://www.zotero.org/download/client/dl?channel=release&platform=linux-x86_64&version=%{version}


BuildRequires:  git
BuildRequires:  gtk3-devel
BuildRequires:  libXt-devel
BuildRequires:  libX11-devel
BuildRequires:  dbus-glib-devel
BuildRequires:  gcc-c++
BuildRequires:  python3

Requires:       hicolor-icon-theme
Requires:       gtk3
Requires:       libXt
Requires:       libX11
Requires:       dbus-glib

%description
Zotero is a powerful reference manager that can be used to manage bibliographic data and related research materials.

%prep
%autosetup -n zotero-%{version}
# Nothing to prep; binary tarball

%build
# No build step needed

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/zotero
tar -xjf %{SOURCE0} -C %{buildroot}/opt/zotero --strip-components=1

# Desktop integration
mkdir -p %{buildroot}%{_datadir}/applications
install -Dm644 %{buildroot}/opt/zotero/zotero.desktop \
    %{buildroot}%{_datadir}/applications/zotero.desktop

# Icons
for size in 16 32 48 128 256 512; do
    mkdir -p %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps
    cp -a %{buildroot}/opt/zotero/chrome/icons/default/default$size.png \
        %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/zotero.png || :
done

%files
%{_bindir}/zotero
%{_datadir}/applications/zotero.desktop
%{_datadir}/zotero/

%changelog
%autochangelog