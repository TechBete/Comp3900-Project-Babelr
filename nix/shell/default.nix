pkgs:
pkgs.mkShell {
  name = "Babelr";
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
        argon2-cffi
        argon2-cffi-bindings
      ]))
  ];
  shellHook = ''
    export PYTHONPATH=$(pwd):$PYTHONPATH
  '';
}
