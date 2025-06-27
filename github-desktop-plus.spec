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

BuildRequires:  gcc-c++, make, python3, git, libX11-devel, gtk3-devel
BuildRequires: nodejs
BuildRequires: npm
BuildRequires: jq

%description
GitHub Desktop Plus provides a GUI for Git and GitHub, simplifying cloning, committing, and pull requests on Linux.

%prep
%autosetup -n %{name}-%{version}

# Patch package.json to set dependencies and disable postinstall
jq '.dependencies["minimatch"] = "3.0.8" |
    .devDependencies["@types/glob"] = "7.2.0" |
    .devDependencies["typescript"] = "^5.0.0" |
    .devDependencies["ts-node"] = "^10.9.2" |
    .scripts.postinstall = "echo \"Skipping postinstall\"" |
    .scripts.build = "npx ts-node script/build.ts"' \
    package.json > package.json.new && mv package.json.new package.json

# Remove conflicting dependencies from dependencies (keep only in devDependencies)
jq 'del(.dependencies["typescript"]) | del(.dependencies["ts-node"])' \
    package.json > package.json.new && mv package.json.new package.json

%build
# Install dependencies
npm install --legacy-peer-deps --no-scripts
# Run build
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