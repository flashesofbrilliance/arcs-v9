# SCAFFOLD - Homebrew is DEFERRED behind the npm release (ADR-82). url + sha256 are
# placeholders: no release tarball is cut yet. Do NOT push this to the tap until the
# user cuts a release and fills the two TODOs below.
#
# Tap: flashesofbrilliance/homebrew-tap  (already exists; do NOT invent homebrew-arcs).
#   brew tap flashesofbrilliance/tap && brew install slop-gate
# Conventions mirror the sibling script tool rosetta-shell.rb: support dirs travel
# into libexec, the runner is symlinked into bin.
#
# NOTE on the tarball: slop-gate's linters live in lib/, which is gitignored and
# vendored by build.sh at pack time. The release tarball MUST be built with lib/
# populated (bash build.sh first); a bare `git archive` omits it and the runner has
# no ../../scripts to fall back to inside libexec.
#
class SlopGate < Formula
  desc "Four-layer slop-free / factuality gate for customer-facing surfaces"
  homepage "https://github.com/flashesofbrilliance/arcs-v9/tree/main/tools/slop-gate"
  # TODO(user): point at the cut release tarball (built with vendored lib/) + real sha256.
  url "https://github.com/flashesofbrilliance/arcs-v9/releases/download/slop-gate-v0.1.0/slop-gate-0.1.0.tar.gz"
  sha256 "0000000000000000000000000000000000000000000000000000000000000000" # TODO(user): real sha256
  version "0.1.0"
  license "MIT"

  depends_on "python@3.12"

  def install
    # Support dirs (lib/, bin/, fixtures/) travel with the runner; the `slop-gate`
    # bash entrypoint resolves lib/ relative to its own path. Match rosetta-shell:
    # install everything into libexec, symlink the entrypoint into Homebrew's bin.
    libexec.install Dir["*"]
    bin.install_symlink libexec/"slop-gate"
  end

  test do
    # self-test proves every deterministic gate fails-on-bad and passes-on-good.
    system bin/"slop-gate", "self-test"
  end
end
