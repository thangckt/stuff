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

BuildRequires:  git
BuildRequires:  nodejs
BuildRequires:  npm
BuildRequires:  python3
Requires:       git
Requires:       nodejs

%description
GitHub Desktop Plus provides a GUI for Git and GitHub, simplifying cloning, committing, and pull requests on Linux.

%prep
%autosetup -n %{name}-%{version}

%build
# Install all dependencies with proper peer deps
npm ci --legacy-peer-deps
# Run production build
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