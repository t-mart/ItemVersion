#!/usr/bin/env bash
#
# Development helpers for working on ItemVersion against a local WoW install.
#
# Usage: scripts/dev.sh <install|uninstall|status|check|format|locales|test|watch|help>
#
# The WoW root is the directory containing _retail_, _classic_ and friends. Set
# it once in .wowroot (gitignored), or override it with the WOW_ROOT env var.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SELF="$REPO_ROOT/scripts/dev.sh"
SOURCE_DIR="ItemVersion"

# Link to the source dir rather than the build output. It is a stable path, so
# it cannot rot the way a version-stamped dist/ path does, and an edit is live
# on the next /reload with no build step. The tradeoff is that packager keywords
# stay unexpanded, so non-enUS locales are empty in a dev install.
LINK_SRC="$REPO_ROOT/$SOURCE_DIR"
LIBS_DIR="$LINK_SRC/Libs"
WOWROOT_FILE="$REPO_ROOT/.wowroot"

FLAVORS=(_retail_ _classic_era_ _classic_ _anniversary_)

WOW_ROOT_RESOLVED=""

die() {
  echo "error: $*" >&2
  exit 1
}

report() {
  printf '  %-14s %s\n' "$1" "$2"
}

# Prints the first line of a config file that is neither blank nor a # comment,
# with surrounding whitespace trimmed. Prints nothing if there is no such line,
# which is the normal state of the checked-in template.
read_config_line() {
  local line

  # The || [[ -n "$line" ]] catches a final line with no trailing newline.
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"

    if [[ -z "$line" || "$line" == "#"* ]]; then
      continue
    fi

    printf '%s' "$line"
    return 0
  done <"$1"
}

# Sets WOW_ROOT_RESOLVED. An env var wins over .wowroot so a one-off run can
# point somewhere else without editing the file.
resolve_wow_root() {
  local root="${WOW_ROOT:-}"

  if [[ -z "$root" && -f "$WOWROOT_FILE" ]]; then
    root="$(read_config_line "$WOWROOT_FILE")"
  fi

  if [[ -z "$root" ]]; then
    echo "error: no WoW root configured." >&2
    echo "Copy the template and set the path for your machine:" >&2
    echo "  cp .wowroot.template .wowroot" >&2
    echo "or pass it directly:" >&2
    echo "  WOW_ROOT='/path/to/World of Warcraft' scripts/dev.sh install" >&2
    exit 1
  fi

  [[ -d "$root" ]] || die "not a directory: $root"

  WOW_ROOT_RESOLVED="$root"
}

require_libs() {
  [[ -d "$LIBS_DIR" ]] || die "$(printf '%s\n%s\n%s' \
    "$SOURCE_DIR/Libs is missing, so the addon would fail to load." \
    "Fetch the Ace3 externals first:" \
    "  make libs")"
}

addons_dir_for() {
  printf '%s' "$WOW_ROOT_RESOLVED/$1/Interface/AddOns"
}

target_for() {
  printf '%s' "$(addons_dir_for "$1")/$SOURCE_DIR"
}

# Prints what is sitting at a target path: absent, link-ok, link-broken, real-dir.
# Tests -L before -e/-d, since both of those follow symlinks.
classify() {
  local target="$1"

  if [[ -L "$target" ]]; then
    if [[ -e "$target" ]]; then
      echo "link-ok"
    else
      echo "link-broken"
    fi
  elif [[ -d "$target" ]]; then
    echo "real-dir"
  else
    echo "absent"
  fi
}

installed_version_at() {
  local toc="$1/$SOURCE_DIR.toc"
  grep -m1 '^## Version:' "$toc" 2>/dev/null | cut -d' ' -f3- || true
}

cmd_install() {
  resolve_wow_root
  require_libs

  local linked=0

  for flavor in "${FLAVORS[@]}"; do
    local addons target
    addons="$(addons_dir_for "$flavor")"
    target="$(target_for "$flavor")"

    if [[ ! -d "$addons" ]]; then
      report "$flavor" "skip, no AddOns dir"
      continue
    fi

    # A real directory is someone else's install. Deleting it is the user's call.
    if [[ "$(classify "$target")" == "real-dir" ]]; then
      report "$flavor" "REFUSED, a real directory is installed there"
      report "" "remove it yourself, then re-run: $target"
      continue
    fi

    # -n so an existing symlink is replaced rather than followed into.
    ln -sfn "$LINK_SRC" "$target"
    report "$flavor" "linked"
    linked=$((linked + 1))
  done

  echo "Linked $linked flavor(s) to $SOURCE_DIR/. Use /reload in game to pick up edits."
}

cmd_uninstall() {
  resolve_wow_root

  for flavor in "${FLAVORS[@]}"; do
    local target
    target="$(target_for "$flavor")"

    case "$(classify "$target")" in
      link-ok | link-broken)
        rm "$target"
        report "$flavor" "unlinked"
        ;;
      real-dir)
        report "$flavor" "left alone, real directory not a symlink"
        ;;
    esac
  done
}

cmd_status() {
  resolve_wow_root
  echo "WOW_ROOT: $WOW_ROOT_RESOLVED"

  for flavor in "${FLAVORS[@]}"; do
    local target
    target="$(target_for "$flavor")"

    case "$(classify "$target")" in
      link-ok)
        report "$flavor" "symlink -> $(readlink "$target")"
        ;;
      link-broken)
        report "$flavor" "BROKEN symlink -> $(readlink "$target")"
        ;;
      real-dir)
        report "$flavor" "real directory, version $(installed_version_at "$target")"
        ;;
      absent)
        report "$flavor" "not installed"
        ;;
    esac
  done
}

require_tool() {
  command -v "$1" >/dev/null || die "$1 is not installed."
}

# selene and stylua resolve their config (selene.toml, stylua.toml,
# .styluaignore) relative to the cwd, so run from the repo root. Nothing here
# short-circuits: one run should report everything that is wrong.
cmd_check() {
  require_tool selene
  require_tool stylua
  require_tool uv
  cd "$REPO_ROOT"

  local failed=0

  selene "$SOURCE_DIR" || failed=1

  if stylua --check "$SOURCE_DIR"; then
    echo "stylua: no changes needed"
  else
    echo "stylua: formatting needed, run 'make format'"
    failed=1
  fi

  # --check so this never edits from a check run. `make locales` is the mode
  # that writes.
  uv run scripts/locales.py --check || failed=1

  return "$failed"
}

# Prunes stale keys, sorts, and stubs out anything untranslated. uv fetches the
# script's dependencies itself, so there is no venv to set up.
cmd_locales() {
  require_tool uv
  cd "$REPO_ROOT"
  uv run scripts/locales.py
}

cmd_test() {
  require_tool uv
  cd "$REPO_ROOT"
  uv run scripts/test_locales.py
}

cmd_format() {
  require_tool stylua
  cd "$REPO_ROOT"
  stylua "$SOURCE_DIR"
  echo "formatted $SOURCE_DIR"
}

# There is no build step to run here: install symlinks the source dir, so a save
# is already live in game. All this does is lint, so a mistake surfaces before
# you alt-tab and reload. watchexec owns the debouncing and the .gitignore
# handling, which keeps Libs/ and .release/ out of the watch set.
cmd_watch() {
  require_tool watchexec

  exec watchexec \
    --watch "$LINK_SRC" \
    --exts lua,toc,xml \
    --debounce 200ms \
    --clear \
    -- "$SELF" check
}

cmd_help() {
  cat <<EOF
Usage: scripts/dev.sh <command>

Commands:
  install     Symlink $SOURCE_DIR/ into each WoW flavor's AddOns dir.
              Refuses to clobber a real directory.
  uninstall   Remove our symlinks. Never touches a real directory.
  status      Show what is installed for each flavor.
  check       Lint with selene, check formatting with stylua, and check the
              locale files. Writes nothing.
  format      Reformat the addon with stylua.
  locales     Prune, sort and stub the locale files. This one writes.
  test        Run the tests for the locale tooling.
  watch       Re-run check on every save. Reload in game to see changes.
  help        Show this message.

The WoW root comes from the WOW_ROOT env var, else from .wowroot.
See .wowroot.template.
EOF
}

main() {
  local command="${1:-help}"

  case "$command" in
    install) cmd_install ;;
    uninstall) cmd_uninstall ;;
    status) cmd_status ;;
    check) cmd_check ;;
    format) cmd_format ;;
    locales) cmd_locales ;;
    test) cmd_test ;;
    watch) cmd_watch ;;
    help | -h | --help) cmd_help ;;
    *)
      echo "error: unknown command: $command" >&2
      echo >&2
      cmd_help >&2
      exit 1
      ;;
  esac
}

main "$@"
