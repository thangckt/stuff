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

BuildRequires:  gcc-c++, make, python3, nodejs, npm, git, libX11-devel, gtk3-devel

%description
GitHub Desktop Plus provides a GUI for Git and GitHub, simplifying cloning, committing, and pull requests on Linux.

%prep
%autosetup -n %{name}-%{version}

# Compatibility workaround for Node.js 22
npm install --legacy-peer-deps minimatch@3.0.8 @types/glob@7.2.0

%build
npm install --legacy-peer-deps
npm run build -- --max_old_space_size=4096

%install
install -d %{buildroot}%{_bindir} \
           %{buildroot}%{_datadir}/%{name} \
           %{buildroot}%{_datadir}/applications

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