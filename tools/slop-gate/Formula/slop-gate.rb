# SCAFFOLD - not tap-ready. url + sha256 are placeholders (no release cut yet),
# license is undecided (see README). Do NOT `brew install` or push this to a tap
# until the user fills the four TODOs below and cuts a release tarball.
#
# Intended tap repo: flashesofbrilliance/homebrew-arcs
#   (Homebrew tap naming: a repo named homebrew-arcs installs via
#    `brew tap flashesofbrilliance/arcs && brew install slop-gate`.)
#   -> tap repo name is an OPEN DECISION for the user; homebrew-arcs is the recommendation.
#
class SlopGate < Formula
  desc "Four-layer slop-free / factuality gate for customer-facing surfaces"
  homepage "https://github.com/flashesofbrilliance/arcs-v9/tree/main/tools/slop-gate"
  # TODO(user): point at a cut release tarball and fill its sha256.
  url "https://github.com/flashesofbrilliance/arcs-v9/releases/download/slop-gate-v0.1.0/slop-gate-0.1.0.tar.gz"
  sha256 "0000000000000000000000000000000000000000000000000000000000000000" # TODO(user): real sha256
  version "0.1.0"
  # TODO(user): choose a license (recommended: MIT). Homebrew wants an SPDX id or :cannot_represent.
  license :cannot_represent

  depends_on "python@3.12"

  def install
    # The tarball is expected to carry the vendored, self-contained layout
    # produced by build.sh: bin/ (the runners) + lib/ (the stdlib-only linters
    # + the rubric). No pip install, no network at build time.
    libexec.install "lib", "bin"
    (bin/"slop-gate").write <<~SH
      #!/bin/bash
      exec "#{libexec}/bin/slop-gate" "$@"
    SH
    chmod 0755, bin/"slop-gate"
  end

  test do
    # self-test proves every deterministic gate fails-on-bad and passes-on-good.
    system bin/"slop-gate", "self-test"
  end
end
