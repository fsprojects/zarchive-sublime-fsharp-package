[![Build status](https://ci.appveyor.com/api/projects/status/uuqaj61vyqwwxqe1/branch/master?svg=true)](https://ci.appveyor.com/project/guillermooo/sublime-fsharp-package/branch/master) [![Build Status](https://travis-ci.org/fsharp/sublime-fsharp-package.svg?branch=master)](https://travis-ci.org/fsharp/sublime-fsharp-package)

# FSharp

Code intelligence for **F# development** in **Sublime Text 3**.


## Features

- Autocompletion
- Live error checking
- Tooltips
- Go to definition
- Show definitions in current file
- Syntax highlighting
- Runs F# scripts in output panel


## Building


#### Cross-platform

- Start Sublime Text
- Press F7
- Select **Build FSharp**


#### Linux/Mac

```shell
./build.sh
```


#### Windows

```shell
build.cmd
```

## Installing


The `install` task
will publish the package
to Sublime Text's *Data* directory,
and restart Sublime Text if it is running.


#### Cross-platform

- Start Sublime Text
- Press F7
- Select **Build FSharp - Publish Locally (Install)**


#### Linux/Mac

```shell
./build.sh install
```


#### Windows

For full installations,
run the following command:

```shell
build.cmd install
```

For portable installations,
you must pass along
the data directory.

```shell
build install sublimeDir="d:\Path\To\Sublime\Text\Data"
```

Optionally, you can set
the `SUBLIME_TEXT_DATA` environment variable,
which should point to the Sublime Text *Data* directory.
If `SUBLIME_TEXT_DATA` is present,
you don't need to pass the `sublimeDir` argument
to the build script.


## Developing FSharp

Pull requests to FSharp welcome!


#### General Steps for Development

* Clone this repository to any folder outside of Sublime Text's *Data* folder
* Edit files as needed
* Close Sublime Text
* Install via `./build.[sh|cmd] install`
* Restart Sublime Text
* Run the tests via command palette: **Build FSharp: Test (All)**
