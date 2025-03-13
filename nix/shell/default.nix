pkgs:
pkgs.mkShell {
  name = "Poincare";
  packages = with pkgs; [
    nixd
    alejandra
    statix
    deadnix
    black
    pyright
    (python3.withPackages (p:
      with p; [
        passlib
        hypothesis
        pytest
      ]))
  ];
  shellHook = ''
    export PYTHONPATH=$(pwd)
    echo "PYTHONPATH set to $(pwd)"
  '';
}
