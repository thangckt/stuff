#!/bin/bash

##### ANCHOR: Info
# This script to update the versions of .spec files in the current directory.

##### ANCHOR: Parameters
### Helper functions
function fetch_gitlab_version() {
    local repo_url="$1"
    local project_path=$(echo "${repo_url#https://gitlab.com/}" | sed 's|/|%2F|g')
    local api_url="https://gitlab.com/api/v4/projects/${project_path}/repository/tags"

    new_version=$(curl -sL "$api_url" | grep -o '"name":"[^"]*"' | head -n1 | sed 's/"name":"v\?\([^"]*\)"/\1/')

    if [[ -z "$new_version" ]]; then
        echo "Failed to get version for $repo_url" >&2
        exit 1
    fi
    echo "$new_version"
}

function fetch_github_version() {
    local repo_url="$1"
    new_version=$(curl -sL "${repo_url}/releases/latest" | sed -nE 's|.*href="[^"]*/tag/v?([0-9]+(\.[0-9]+)*)".*|\1|p' | head -n1)
    if [[ -z "$new_version" ]]; then
        echo "Failed to get version for $repo_url" >&2
        exit 1
    fi
    echo "$new_version"
}

function update_spec_version() {
    local spec_file="$1"
    local new_version="$2"

    current_version=$(grep -E '^Version:' "$spec_file" | awk '{print $2}')
    # Compare versions using sort -V (version sort)
    if [[ "$new_version" != "$current_version" ]] && [[ "$(printf "%s\n%s" "$current_version" "$new_version" | sort -V | tail -n1)" == "$new_version" ]]; then
        echo "Updating version $current_version to $new_version, in file $spec_file"
        sed -i "s/^Version:[[:space:]]\+$current_version/Version:        $new_version/" "$spec_file"
    else
        echo "Version ($current_version) is up to date, in file $spec_file"
    fi
}

##### SECTION: From GitHub
##### ANCHOR: rustdesk
repo_url="https://github.com/rustdesk/rustdesk"
spec_files="rebuildRPM_rustdesk.spec"

new_version=$(fetch_github_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

##### ANCHOR: electerm
repo_url="https://github.com/electerm/electerm"
spec_files="rebuildRPM_electerm.spec"

new_version=$(fetch_github_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

##### ANCHOR: github-desktop
repo_url="https://github.com/pol-rivero/github-desktop-plus"
spec_files="rebuildRPM_github-desktop-plus.spec"

new_version=$(fetch_github_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

##### ANCHOR: goldendict
repo_url="https://github.com/goldendict/goldendict"
spec_files="goldendict.spec"

new_version=$(fetch_github_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

##### ANCHOR: rssguard
repo_url="https://github.com/martinrotter/rssguard"
spec_files="rssguard.spec"

new_version=$(fetch_github_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

##### ANCHOR: Ovito
repo_url="https://gitlab.com/stuko/ovito"
spec_files="ovito.spec"
new_version=$(fetch_gitlab_version "$repo_url")
update_spec_version "$spec_files" "$new_version"

##### ANCHOR: Zotero
##### !SECTION
