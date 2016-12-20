[![Build status](https://ci.appveyor.com/api/projects/status/uuqaj61vyqwwxqe1/branch/master?svg=true)](https://ci.appveyor.com/project/guillermooo/sublime-fsharp-package/branch/master) [![Build Status](https://travis-ci.org/fsharp/sublime-fsharp-package.svg?branch=master)](https://travis-ci.org/fsharp/sublime-fsharp-package)

# FSharp

Code intelligence for **F# development** in **Sublime Text 3**.


## Features

- Autocompletion
- Live error checking
- Tooltips (CTRL k i)
- Go to definition
- Show definitions in current file
- Syntax highlighting
- Runs F# scripts in output panel


## Main Keyboard Shortcuts

Keyboard Shortcut   | Action
------------------ | ------------- |
<kbd>Ctrl+.</kbd>, <kbd>Ctrl+.</kbd> | Show F# commands
<kbd>Ctrl+.</kbd>, <kbd>Ctrl+o</kbd> | Show last output panel
<kbd>Ctrl+k</kbd>, <kbd>Ctrl+i</kbd> | Show tooltip for symbol
<kbd>F12</kbd> | Go to definition
<kbd>Ctrl+space</kbd> | Open autocomplete list


## Building


#### Cross-platform

- Start Sublime Text
- Press <kbd>F7</kbd>
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
- Press <kbd>F7</kbd>
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

Maintainers
-----------

Tha maintainers of this repository appointed by the F# Core Engineering Group are:

 - [Robin Neatherway](https://github.com/rneatherway), [Steffen Forkmann](http://github.com/forki), [Karl Nilsson](http://github.com/kjnilsson), [Dave Thomas](http://github.com/7sharp9) and [Guillermo López-Anglada](http://github.com/guillermooo)
 - The primary maintainer for this repository is [Guillermo López-Anglada](http://github.com/guillermooo)
