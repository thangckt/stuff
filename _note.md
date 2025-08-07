# Use Copr to build a package for Fedora

This file contains the `.spec` files for building multiple packages using Copr.

See https://copr.fedorainfracloud.org/coprs/thangckt/multi_packages


# Official Fedora build system
- Koji: https://koji.fedoraproject.org/koji/packages

How to get the spec file for a package:
- Search for the package on the Koji website.
- Click on the package name to view its details.
- Look for `Source	git+https://src.fedoraproject.org/rpms/evolution.git` or similar lines.
- Just go to: `https://src.fedoraproject.org/rpms/evolution` -> `files` to see the spec file.


# Some spec repos:
- https://github.com/PhantomX/chinforpms


# Sections in spec files

## Auto replacement
- Add `Provides: <package_name>`: Let other packages know the `spec-package` (building from spec) can replace the `<package_name>`
- Add `Obsoletes: <package_name> <version>`: Replace the `<package_name>` by the `spec-package`. `Obsoletes` does not accept wildcards.
- Add `Conflicts: <package_name> <version>`: Protect mechanism, to prevent installation of the `spec-package` if `<package_name>` is already installed, and vice versa. Need manually remove the conflicting package first.
    - Should not use `Conflicts`, since it can prevent install dependencies. Use `Obsoletes` instead.
```sh
## Replace and protect from conflicting (complicated, avoid using this)
Provides:       texlive, texlive-*

Obsoletes:      texlive <= %{version}
Obsoletes:      texlive-base <= %{version}
Obsoletes:      texlive-kpathsea <= %{version}
Obsoletes:      texlive-latex <= %{version}
Obsoletes:      texlive-scheme-full <= %{version}
```



# `Texlive`
- Install `texlive` using `install-tl` script.

The concepts between *compile-time paths* and *runtime paths*. If compile errors related to {%buildroot} being in paths, it means one of two things:
1. The TeX Live installer itself is generating incorrect, hardcoded paths. This is a less common scenario for a robust installer like `install-tl`, which is designed to handle `DESTDIR` environments.
2. The build process or a subsequent check is finding {%buildroot} in a file that it shouldn't, and this is being flagged as an error. This is the more likely scenario.

TeX Live's installer defaults to `/usr/local/texlive/<year>`, but the `%install` section of an RPM must install into `%{buildroot}` only.
This is the critical line from the log:
```
mkdir(/usr/local/texlive/) failed: Permission denied
```
RPM doesn’t allow writes to `/usr/local/` during `%install`.




There are 2 ways to set ENV paths for `texlive` packages:
1. Use `alternaives` to set the default path. (avoid using this method)
- Some packages may not work properly with this method.
```sh
%post
## registers each binary file in opt/ folder of TeX Live 2025
for bin_path in /opt/texlive/%{version}/bin/x86_64-linux/*; do
    [ -f "$bin_path" ] || continue
    bin_name=$(basename "$bin_path")
    # Prefer non-dev version by priority
    if [[ "$bin_name" == *-dev ]]; then
        priority=90
    else
        priority=100
    fi
    alternatives --install /usr/bin/$bin_name $bin_name "$bin_path" $priority || :
done

%preun
## Only if uninstalling
if [ "$1" -eq 0 ]; then
    for bin_path in /opt/texlive/%{version}/bin/x86_64-linux/*; do
        [ -f "$bin_path" ] || continue
        bin_name=$(basename "$bin_path")
        # Only remove if this path is currently registered
        if alternatives --display "$bin_name" | grep -q "$bin_path"; then
            alternatives --remove "$bin_name" "$bin_path" || :
        fi
    done
fi
```
2. Use `PATH` environment variable to set the default path (recommended for texlive install-tl).
- Must ensure both `login` and `non-login` shells are configured.
```sh
%install

## other install here

## export environment variables (PATH, MANPATH, etc.) (not use).
mkdir -p %{buildroot}/etc/profile.d
cat > %{buildroot}/etc/profile.d/texlive.sh <<EOF
export PATH=/opt/texlive/%{version}/bin/x86_64-linux:\$PATH
export MANPATH=/opt/texlive/%{version}/texmf-dist/doc/man:\$MANPATH
export INFOPATH=/opt/texlive/%{version}/texmf-dist/doc/info:\$INFOPATH
EOF

## New section to ensure non-login shells also get the PATH
mkdir -p %{buildroot}/etc/bashrc.d
cat > %{buildroot}/etc/bashrc.d/texlive.sh <<EOF
# Source the profile.d script for interactive non-login shells
if [ -f /etc/profile.d/texlive.sh ]; then
  . /etc/profile.d/texlive.sh
fi
EOF


%post
# Inform the user how to activate immediately
echo "======================================================="
echo "TeX Live has been installed to %{install_dir}."
echo "To take affect, open a new terminal session, or try to source this script manually:"
echo "  source /etc/profile.d/texlive.sh"
echo "======================================================="

%files
/opt/texlive
%config(noreplace) /etc/profile.d/texlive.sh
%config(noreplace) /etc/bashrc.d/texlive.sh
```
- Also need to see `env` in `latex-workshop` to work properly.
```js
"latex-workshop.latex.tools": [
    "env": {
        "PATH": "/opt/texlive/%{version}/bin/x86_64-linux:${env:PATH}"
    }
  ]
"
```
## Issue with `tlmgr`
`tlmgr` is the TeX Live Manager, used to manage/update Tex Live packages.

There is a problem that wrong `tlmgr` is used with and without `sudo`. So can not use `tlmgr` to update packages properly.
```sh
$ which tlmgr
/opt/texlive/2025/bin/x86_64-linux/tlmgr
$ sudo which tlmgr
/usr/sbin/tlmgr
```
Solve this by create a wrapper script for `tlmgr` (in most system, `/usr/local/bin` is before `/usr/bin` in PATH)
```sh
## Create wrapper for tlmgr to override system /usr/sbin/tlmgr
install -Dpm755 /dev/stdin %{buildroot}/usr/local/bin/tlmgr <<'EOF'
#!/bin/sh
exec %{install_dir}/bin/x86_64-linux/tlmgr "$@"
EOF
```
## Perl issue
When TeX Live is installed, it often includes its own Perl distribution and a set of Perl modules that are essential for its operation. The `PERL5LIB` environment variable specifies a list of directories where Perl should look for modules.
```sh
install_dir=/opt/texlive/%{version}
export PERL5LIB=%{install_dir}/tlpkg:%{install_dir}/texmf-dist/scripts:%{install_dir}/texmf-dist
```
## `latexindent` issue
TeX Live includes `latexindent.pl` but not all of its dependencies. You must either:
- Add the missing Perl modules yourself, or
- Use the system’s `latexindent.pl` (should avoid, since it install Perl modules and many other dependencies).

This is cause of issue: `Can't locate YAML/Tiny.pm in @INC (you may need to install the YAML::Tiny module)...`

TeX Live upstream (via `install-tl`) includes:
- `latexindent.pl` in `texmf-dist/scripts/latexindent/`
- `.pm` files in `texmf-dist/scripts/latexindent/LatexIndent/*.pm`

But does not include the external Perl modules like: `YAML::Tiny`, `File::HomeDir`, `Unicode::GCString`

> Solution: Download required Perl modules manually
```sh
%prep
# Download missing Perl modules for latexindent.pl
mkdir -p missing_perl_modules/YAML
curl -L -o missing_perl_modules/YAML/Tiny.pm https://raw.githubusercontent.com/Perl-Toolchain-Gang/YAML-Tiny/main/lib/YAML/Tiny.pm

mkdir -p missing_perl_modules/File
curl -L -o missing_perl_modules/File/HomeDir.pm https://raw.githubusercontent.com/Perl-Toolchain-Gang/File-HomeDir/main/lib/File/HomeDir.pm

mkdir -p missing_perl_modules/Unicode
curl -L -o missing_perl_modules/Unicode/GCString.pm https://raw.githubusercontent.com/Perl-Toolchain-Gang/Unicode-GCString/main/lib/Unicode/GCString.pm

%install
# Install the missing Perl modules for latexindent
mkdir -p %{buildroot}%{install_dir}/texmf-dist/scripts/latexindent
cp -a missing_perl_modules/* %{buildroot}%{install_dir}/texmf-dist/scripts/latexindent/
```

# rustdesk
- version 1.4.1 is very slow on the client side, so use version 1.4.0 instead.