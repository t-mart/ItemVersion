#!/usr/bin/env bash
set -euo pipefail

# goal: run release.sh but with cached libs
# downloading the libs each time is slow, really drags down developer experience
# logic:
# if ItemVersion/Libs exists
#   just run `release.sh -sz`
#   then, copy the cached libs into .release/ItemVersion/Libs
# else
#   run `release.sh -z`, which downloads the libs into .release/ItemVersion/Libs (and of course builds the addon)
#   copy .release/ItemVersion/Libs to ItemVersion/Libs
# done

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

if [ -d "ItemVersion/Libs" ]; then
  echo "Using cached libs from ItemVersion/Libs"

  # Run release.sh without downloading libs (-s for skip externals)
  release.sh -sz

  # Copy cached libs into the release directory
  echo "Copying cached libs to .release/ItemVersion/Libs"
  cp -r ItemVersion/Libs .release/ItemVersion/
else
  echo "No cached libs found, downloading libs"

  # Run release.sh with lib downloads
  release.sh -z

  # Cache the libs for future builds
  echo "Caching libs to ItemVersion/Libs for future builds"
  cp -r .release/ItemVersion/Libs ItemVersion/
fi