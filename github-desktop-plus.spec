Name:           github-desktop-plus
Version:        0.4.21
Release:        1%{?dist}
Summary:        GitHub Desktop Plus, a GUI client for Git and GitHub

License:        MIT
URL:            https://github.com/pol-rivero/github-desktop-plus
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  nodejs npm git

%description
GitHub Desktop Plus provides a GUI for Git and GitHub, simplifying cloning, committing, and pull requests on Linux.

%prep
%autosetup -n %{name}-%{version}

# Create minimal git repo for build script
git init
git config user.name "builder"
git config user.email "builder@localhost"
git add .
git commit -m "build"

%build
npm install --legacy-peer-deps
npm run build

%install
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -r dist/* %{buildroot}%{_datadir}/%{name}/

%files
%{_datadir}/%{name}/

%changelog
%autochangelog