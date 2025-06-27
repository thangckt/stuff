Name:           github-desktop-plus
Version:        0.4.21
Release:        1%{?dist}
Summary:        GitHub Desktop Plus, a GUI client for Git and GitHub

License:        MIT
URL:            https://github.com/pol-rivero/github-desktop-plus
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  nodejs npm git python3 gcc-c++ make
Requires:       git

%description
GitHub Desktop Plus provides a GUI for Git and GitHub, simplifying cloning,
committing, and pull requests on Linux.

%prep
%autosetup -n %{name}-%{version}

# Initialize a minimal git repo to satisfy build requirements
git init
git config user.email "builder@localhost"
git config user.name "RPM Builder"
git add .
git commit -m "Initial commit for build"

%build
# Set environment for Node.js build
export PYTHON=/usr/bin/python3
export NODE_OPTIONS="--max_old_space_size=4096"

# Install dependencies with legacy peer deps support
npm install --legacy-peer-deps --no-scripts

# Run the build process
npm run build -- --max_old_space_size=4096

%install
# Create application directory
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_bindir}

# Copy built application files
cp -r dist/* %{buildroot}%{_datadir}/%{name}/

# Create a simple launcher script
cat > %{buildroot}%{_bindir}/%{name} << 'EOF'
#!/bin/bash
exec %{_datadir}/%{name}/github-desktop-plus "$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

%files
%{_datadir}/%{name}/
%{_bindir}/%{name}

%changelog
%autochangelog