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

    renovate.package = lib.mkPackageOption pkgs "renovate" {};

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
