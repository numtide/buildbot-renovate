{config, pkgs, lib, ...}:
let
  cfg = config.services.buildbot-renovate;
in
{
  options.services.buildbot-renovate = {
    enable = lib.mkEnableOption "Buildbot renovate integration";

    package = lib.mkOption {
      default = ps: ps.callPackage ../../package.nix {};
    };

    renovate.package = lib.mkOption {
      type = lib.types.package;
      default =
        if cfg.renovate.nixPatch
        then pkgs.renovate.overrideAttrs (
          final: _prev:
          {
            src = pkgs.fetchFromGitHub {
              owner = "renovatebot";
              repo = "renovate";
              rev = "499c353780dce0df80fb44f84918c512a00d4ba1";
              hash = "sha256-ePNar0asjwfMvNVz/N32hYneim13/Q1jOLXFbyZaDkY=";
            };

            pnpmDeps = pkgs.pnpm_10.fetchDeps {
              inherit (final) pname version src;
              hash = "sha256-tf7WO/i9pFW+FNNqqPGuZE5mkJ841OgM3sqIZ8ZnU0g=";
            };
          }
        )
        else pkgs.renovate;
    };

    renovate.nixPatch = lib.mkEnableOption "Include Nix support patch in renovate";
  };

  config = lib.mkIf cfg.enable {
    systemd.services.buildbot-worker.path = [
      cfg.renovate.package
    ];
    services.buildbot-master = {
      extraImports = ''
        import buildbot_renovation
      '';
      configurators = [
        "buildbot_renovation.BuildbotRenovation()"
      ];
      pythonPackages = ps: lib.singleton (cfg.package ps);
    };
  };
}
