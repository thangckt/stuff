Name:           github-desktop-plus
Version:        0.4.21
Release:        1%{?dist}
Summary:        GitHub Desktop Plus, a GUI client for Git and GitHub

License:        MIT
URL:            https://github.com/pol-rivero/github-desktop-plus
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

%if 0%{?fedora} > 41
ExcludeArch:   %{ix86}
%endif

BuildRequires:  gcc-c++, gtk3-devel, libX11-devel
BuildRequires:  nodejs
BuildRequires:  npm

%description
GitHub Desktop Plus provides a GUI for Git and GitHub via Electron, packaging already built JS in the `dist/` directory.

%prep
%autosetup -n %{name}-%{version}

# No build necessary — shipping prebuilt assets

%build
# skip building, use dist/ provided in the tarball

%install
install -d %{buildroot}%{_bindir} \
           %{buildroot}%{_datadir}/%{name} \
           %{buildroot}%{_datadir}/applications

# Copy prebuilt Electron app
cp -r dist/* %{buildroot}%{_datadir}/%{name}/

install -m 644 assets/%{name}.desktop \
        %{buildroot}%{_datadir}/applications/%{name}.desktop

install -D -m755 scripts/launcher.sh \
        %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop

%changelog
%autochangelog