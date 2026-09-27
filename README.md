# T3 Code for Nix

This flake packages upstream's Linux desktop AppImages. It pins the latest stable
and nightly releases independently, without waiting for nixpkgs to update its
T3 Code build.

```sh
nix run path:.#stable
nix run path:.#nightly
```

To install one in your profile, use `nix profile install path:.#stable` or
`nix profile install path:.#nightly`. The stable package is also `#default`.

In another flake, add this repository as an input and select
`inputs.t3code.packages.${pkgs.system}.stable` or `.nightly` in
`environment.systemPackages` or `home.packages`. The desktop commands are
`t3code` and `t3code-nightly`, so both can be installed together.

The [update workflow](.github/workflows/update.yml) checks upstream releases at
minute 17 every three hours (UTC) and commits new version and SHA-256 pins to
the default branch. GitHub scheduled workflows can be delayed; an update also
requires the workflow to be enabled and Actions to have permission to write to
the repository. Run `python3 scripts/update-releases.py` for a manual check, or
trigger the workflow with **Run workflow**. Consumers update their flake lock
or profile to pick up a new commit; Nix does not silently change a pinned build.

Upstream release artifacts: <https://github.com/pingdotgg/t3code/releases>.
The packages currently target `x86_64-linux` and `aarch64-linux`.
