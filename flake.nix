{
  description = "T3 Code stable and nightly desktop releases for NixOS";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { nixpkgs, ... }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f (import nixpkgs { inherit system; }));
      releases = builtins.fromJSON (builtins.readFile ./releases.json);
      archNames = {
        x86_64-linux = "x86_64";
        aarch64-linux = "arm64";
      };
      makePackage = pkgs: channel:
        let
          system = pkgs.stdenv.hostPlatform.system;
          release = releases.${channel};
          pname = if channel == "stable" then "t3code" else "t3code-nightly";
          asset = "T3-Code-${release.version}-${archNames.${system}}.AppImage";
          src = pkgs.fetchurl {
            url = "https://github.com/pingdotgg/t3code/releases/download/${release.tag}/${asset}";
            hash = release.hashes.${system};
          };
          contents = pkgs.appimageTools.extract {
            inherit pname src;
            inherit (release) version;
          };
          desktopItem = pkgs.makeDesktopItem {
            name = pname;
            desktopName = if channel == "stable" then "T3 Code" else "T3 Code Nightly";
            exec = "${pname} %U";
            icon = pname;
            comment = "Control coding agents";
            categories = [ "Development" ];
            terminal = false;
          };
        in
        pkgs.appimageTools.wrapType2 {
          inherit pname src;
          inherit (release) version;
          extraInstallCommands = ''
            mkdir -p "$out/share/applications" "$out/share/icons/hicolor/128x128/apps"
            cp ${desktopItem}/share/applications/*.desktop "$out/share/applications/"
            icon=$(find ${contents} -type f \( -name 'icon.png' -o -name '*.png' \) | head -n 1)
            if [ -n "$icon" ]; then
              cp "$icon" "$out/share/icons/hicolor/128x128/apps/${pname}.png"
            fi
          '';
          meta = with pkgs.lib; {
            description = "T3 Code ${channel} desktop app";
            homepage = "https://t3.codes";
            downloadPage = "https://github.com/pingdotgg/t3code/releases/tag/${release.tag}";
            license = licenses.mit;
            platforms = systems;
            mainProgram = pname;
          };
        };
    in
    {
      packages = forAllSystems (pkgs:
        let
          stable = makePackage pkgs "stable";
          nightly = makePackage pkgs "nightly";
        in
        {
          default = stable;
          inherit stable nightly;
        });
    };
}
