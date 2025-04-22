{ buildPythonPackage, hatchling }:
buildPythonPackage {
  pname = "buildbot-renovation";
  version = "none";

  format = "pyproject";

  buildInputs = [
    hatchling
  ];

  src = ./.;
}
