#!/bin/bash

#####ANCHOR Info
# This script to update the versions of .spec files in the current directory.

#####ANCHOR Parameters
### Helper functions
fetch_gitlab_version() {
    # There are 2 types of GitLab repositories:
    # 1. https://gitlab.com/username/repo -> use tags: (/api/v4/projects/:id/repository/tags)
    # 2. https://gitlab.com/namespace/project -> use releases (/api/v4/projects/:id/releases)

    local repo_url="$1"
    local project_path
    project_path=$(echo "${repo_url#https://gitlab.*/}" | sed 's|/|%2F|g')
    local base_api_url="${repo_url%%://*}://$(echo "$repo_url" | cut -d/ -f3)/api/v4/projects/${project_path}"

    local new_version
    # Try to fetch from /releases
    new_version=$(curl -sL "${base_api_url}/releases" | grep -oP '"tag_name":"v?\K[^"]+' | head -n1)
    # If no releases, fall back to /repository/tags
    if [[ -z "$new_version" ]]; then
        new_version=$(curl -sL "${base_api_url}/repository/tags" | grep -oP '"name":"v?\K[^"]+' | head -n1)
    fi
    if [[ -z "$new_version" ]]; then
        echo "Failed to get version for $repo_url" >&2
        return 1
    fi

    echo "$new_version"
}

function fetch_github_version() {
    local repo_url="$1"
    local new_version
    new_version=$(curl -sL "${repo_url}/releases/latest" | sed -nE 's|.*href="[^"]*/tag/v?([0-9]+(\.[0-9]+)*)".*|\1|p' | head -n1)
    if [[ -z "$new_version" ]]; then
        echo "Failed to get version for $repo_url" >&2
        exit 1
    fi
    echo "$new_version"
}

fetch_zotero_version() {
    local url="https://www.zotero.org/download/client/dl?channel=release&platform=linux-x86_64"
    local final_url

    final_url=$(curl -Ls -o /dev/null -w "%{url_effective}" "$url")
    # Example: https://download.zotero.org/client/release/6.0.37/Zotero-6.0.37_linux-x86_64.tar.bz2
    local new_version
    new_version=$(echo "$final_url" | sed -nE 's|.*/release/([0-9.]+)/.*|\1|p')
    if [[ -z "$new_version" ]]; then
        echo "Failed to extract Zotero version from redirect" >&2
        return 1
    fi
    echo "$new_version"
}

function update_spec_version() {
    local spec_file="$1"
    local new_version="$2"

    current_version=$(grep -E '^Version:' "$spec_file" | awk '{print $2}')
    # Compare versions using sort -V (version sort)
    if [[ "$new_version" != "$current_version" ]] && [[ "$(printf "%s\n%s" "$current_version" "$new_version" | sort -V | tail -n1)" == "$new_version" ]]; then
        sed -i "s/^Version:[[:space:]]\+$current_version/Version:        $new_version/" "$spec_file"
    else
        new_version=""
    fi
    printf "%-15s %-15s %s\n" "$current_version" "$new_version" "$spec_file"
}

#####SECTION: From GitHub
printf "%-15s %-15s %s\n" "Old_ver" "New_ver" "File"

#####ANCHOR rustdesk
repo_url="https://github.com/rustdesk/rustdesk"
spec_files="rebuildRPM_rustdesk.spec"
new_version=$(fetch_github_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

#####ANCHOR electerm
repo_url="https://github.com/electerm/electerm"
spec_files="rebuildRPM_electerm.spec"
new_version=$(fetch_github_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

#####ANCHOR github-desktop
repo_url="https://github.com/pol-rivero/github-desktop-plus"
spec_files="rebuildRPM_github-desktop-plus.spec"
new_version=$(fetch_github_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

#####ANCHOR goldendict
repo_url="https://github.com/goldendict/goldendict"
spec_files="goldendict.spec"
new_version=$(fetch_github_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

#####ANCHOR rssguard
repo_url="https://github.com/martinrotter/rssguard"
spec_files="rssguard.spec"
new_version=$(fetch_github_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

#####ANCHOR zed
repo_url="https://github.com/zed-industries/zed"
spec_files="zed.spec"
new_version=$(fetch_github_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

#####ANCHOR vscodium
repo_url="https://github.com/VSCodium/vscodium"
spec_files="codium.spec"
new_version=$(fetch_github_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

#####ANCHOR pdf4qt
repo_url="https://github.com/JakubMelka/PDF4QT"
spec_files="pdf4qt.spec"
new_version=$(fetch_github_version "$repo_url")
update_spec_version "$spec_files" "$new_version"


#####ANCHOR Ovito
repo_url="https://gitlab.com/stuko/ovito"
spec_files="ovito.spec"
new_version=$(fetch_gitlab_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

#####ANCHOR FreeFileSync
repo_url="https://gitlab.com/opensource-tracking/FreeFileSync"
spec_files="freefilesync.spec"
new_version=$(fetch_gitlab_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

#####ANCHOR Evolution
repo_url="https://gitlab.gnome.org/GNOME/evolution"
spec_files="evolution2.spec"
new_version=$(fetch_gitlab_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

repo_url="https://gitlab.gnome.org/GNOME/evolution-data-server"
spec_files="evolution1-data-server.spec"
new_version=$(fetch_gitlab_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

repo_url="https://gitlab.gnome.org/GNOME/evolution-ews"
spec_files="evolution3-ews.spec"
new_version=$(fetch_gitlab_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

#####ANCHOR Zotero
spec_files="tarball_zotero.spec"
new_version=$(fetch_zotero_version)
update_spec_version "$spec_files" "$new_version"
#####!SECTION
