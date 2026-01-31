# C language tools folder

## Mandatory Elements

### parse.sh
Thin wrapper on top of real parsing logic.
Under the hood it calls all necessary language specific tooling to parse source code in to AST.

Inputs:
    - Path to `.c` file
    - Path for `.json` file to write result AST to.
Ouptut:
    - No

### compile.sh 
This wrapper on top of language specofoc compilation tools.
Under the hood it should compile provided sopurces in to shared library, so it can be imported in to the test framework for comparison.

Inputs:
    - Path to `.c` file
    - Path to `.c.so` file to create
Action:
    - Compile C code into share library and save as a `.c.so`
Ouptut:
    - No
Example:
    For the file `/foo/bar.c` we should call `./compile.sh /foo/bar.c /foo/bar.c.so` as a result we will get `/foo/bar.c.so` file created

### Toolbox folder
Folder which stores all language specific tools we need. Content of this folder will vary from language to language by alot.
The only file which must be present is this folder is `README.md`, it should explain content of the folder and any actions which maybe required to make it work such as dependencies, build proces etc


### README.md
File which provide explanations on the content of the folder. It also may describe some language specific things which maybe important while we are workign with this language.