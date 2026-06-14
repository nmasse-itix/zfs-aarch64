# Common code shared between build.sh and update.sh

# Prints the list of currently maintained Fedora versions (e.g. "42 43 44"),
# based on the Bodhi releases API.
get_fedora_versions () {
  curl -fsSL "https://bodhi.fedoraproject.org/releases/?exclude_archived=true&state=current" \
    | jq -r '.releases[] | select(.id_prefix=="FEDORA") | .version' \
    | grep -E '^[0-9]+$' | sort -n
}
