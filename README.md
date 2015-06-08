[![Build status](https://ci.appveyor.com/api/projects/status/uuqaj61vyqwwxqe1/branch/master?svg=true)](https://ci.appveyor.com/project/guillermooo/sublime-fsharp-package/branch/master) [![Build Status](https://travis-ci.org/fsharp/sublime-fsharp-package.svg?branch=master)](https://travis-ci.org/fsharp/sublime-fsharp-package)

# FSharp

Support for F# development in Sublime Text 3.
The FSharp package
is only compatible
with **Sublime Text 3**.


## Building


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
to Sublime Text's *Data* directory.


#### Linux/Mac

```shell
./build.sh install
```


## Windows

```shell
build.cmd install
```

For portable installations of Sublime Text
(Windows only),
you must pass along
the data directory.

```shell
build install sublimeDir="d:\Path\To\Sublime\Text\Data"
```


## Developing FSharp

Pull requests to FSharp welcome!


#### General Steps for Development

* Clone this repository to any folder outside of Sublime Text's *Data* folder
* Edit files as needed
* Close Sublime Text
* Install via `./build.[sh|cmd] install`
* Restart Sublime Text
* Run the tests via command palette: **FSharp: Test (All)**
