{
  outputs = inputs@{ self, ... }:
    {
      nixosModules.default = self.nixosModules.buildbot_renovation;
      nixosModules.buildbot_renovation = ./nixos/modules/buildbot_renovation.nix;
    };
}
