[![Build status](https://ci.appveyor.com/api/projects/status/uuqaj61vyqwwxqe1/branch/master?svg=true)](https://ci.appveyor.com/project/guillermooo/sublime-fsharp-package/branch/master)

## FSharp

This package provides support
for F# development in Sublime Text 3.

FSharp is only compatible
with **Sublime Text 3**.

///

**FSharp is currently a preview
and not ready for use**.
If you want to contribute to its development,
you can read on
to learn how to set up
a development environment.

///


### Developing FSharp

Pull requests to FSharp welcome!


### Building

#### Linux/Mac

```shell
./build.sh
```

#### Windows

```shell
build.cmd
```

### Installing

The **Install** build target
will publish the package
to Sublime Text's *Data* directory:

```shell
./build.sh install
```

For portable installations of Sublime Text
(Windows only),
you must pass along
the data directory:

```shell
build install sublimeDir="d:\Path\To\Sublime\Text\Data"
```

#### General Steps for Development

* Clone this repository to any folder outside of Sublime Text's *Data* folder
* Edit files as needed
* Install: `./build.[sh|cmd] install [sublimeDir=d:\Path\To\Sublime\Text\Data]`
* Restart Sublime Text
* Run the tests via command palette: **FSharp: Test (All)**
