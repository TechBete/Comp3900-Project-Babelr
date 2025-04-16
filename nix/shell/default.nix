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
        flask # handles web requests
        flask-cors # handles CORS requests
        flask-restful # handles RESTful API requests
        flask-sqlalchemy # handles database requests
        psycopg2-binary # change this to full psycopg2 library for prod
        python-dotenv # handles environment variables
        typing # handles type hinting
        passlib # handles password hashing
        jinja2 # handles HTML templating
        flask-mail # handles email sending
        flask-jwt-extended # handles JWT token generation
        hypothesis # handles testing
        pytest # handles testing
        argon2_cffi # handles password hashing
        email-validator # handles email validation
        sqlalchemy # handles database requests, duplicate of flask-sqlalchemy
        filetype # helps to check and manage filetypes of audio file
      ]))
  ];
  shellHook = ''
    export PYTHONPATH=$(pwd):$PYTHONPATH
  '';
}
