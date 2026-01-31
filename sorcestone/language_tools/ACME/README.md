# ACME language tools folder
This is not a real language. This folder demonstrates reference structure of the folder

## Mandatory Elements

### parse.sh
Thin wrapper on top of real parsing logic, which migh be complex.
Under the hood it should call all necessary language specific tooling to parse source code in to AST.

Inputs:
    - something ???
    - Path for the AST file to create
Actions:
    -
### compile.sh 
This wrapper on top of language specofoc compilation tools.
Under the hood it should compile provided sopurces in to shared library, so it can be imported in to the test framework for comparison.

Inputs:
    - Path to source file
    - Path to shared library file to create
Actions:
    - Compile code into share library and save into the shared library

### Toolbox folder
Folder which stores all language specific tools we need. Content of this folder will vary from language to language by alot.
The only file which must be present is this folder is `README.md`, it should explain content of the folder and any actions which maybe required to make it work such as dependencies, build proces etc

### README.md
File which provide explanations on the content of the folder. It also may describe some language specific things which maybe important while we are workign with this language.