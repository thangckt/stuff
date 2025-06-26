%global __python        %__python3
%global python          python3
%global python_pfx      python3
%global rpm_python      python3-rpm
%global sitelib         %python3_sitelib

%global copr_common_version 0.21.1.dev


Name:           ovito
Version:        3.12.4
Release:        1%{?dist}
Summary:        OVITO - Open Visualization Tool

License:        MIT
URL:            https://gitlab.com/stuko/ovito
Source0:        %{url}/-/tag/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  git
BuildRequires:  nodejs
BuildRequires:  npm
BuildRequires:  python3
Requires:       git
Requires:       nodejs

%description
OVITO is a scientific data visualization and analysis software for atomistic, molecular and other particle-based simulations.

%prep
%autosetup -n %{name}-%{version}

%build
npm install @types/glob
npm install --production --legacy-peer-deps
npm run build

%install
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -r dist/* %{buildroot}%{_datadir}/%{name}

mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop << 'EOF'
[Desktop Entry]
Name=GitHub Desktop Plus
Exec=%{_bindir}/%{name}
Type=Application
Terminal=false
EOF

mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} << 'EOF'
#!/bin/sh
node %{_datadir}/%{name}/main.js "$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop

%changelog
%autochangelog