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

BuildRequires:  gcc
BuildRequires: gcc-c++
BuildRequires: make
BuildRequires:  libstdc++-devel
BuildRequires:  python3
BuildRequires:  nodejs
BuildRequires:  npm
BuildRequires:  git
BuildRequires:  libX11-devel
BuildRequires:  libXScrnSaver-devel
BuildRequires:  libxkbfile-devel
BuildRequires:  gtk3-devel

%description
GitHub Desktop Plus provides a GUI for Git and GitHub, simplifying cloning, committing, and pull requests on Linux.

%prep
%autosetup -n %{name}-%{version}

%build
npm install @types/glob@7.2.0 --legacy-peer-deps --save-dev
npm install --legacy-peer-deps
npm run build -- --max_old_space_size=4096

%install
install -d %{buildroot}%{_bindir} %{buildroot}%{_datadir}/%{name} %{buildroot}%{_datadir}/applications

# Copy built payload
cp -r dist/* %{buildroot}%{_datadir}/%{name}/

# Desktop entry
install -m 644 %{SOURCE0_DIR}/assets/%{name}.desktop %{buildroot}%{_datadir}/applications/%{name}.desktop

# Wrapper script
install -D -m755 -p %{SOURCE0_DIR}/scripts/launcher.sh %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop

%changelog
%autochangelog