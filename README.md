## FSharp - An F# Package for Sublime Text

This package provides support for F# development in Sublime Text.

FSharp is currently a preview and not ready for use. If you want to
contribute to its development, you can read on to learn how to set up a
development environment.


### Developing FSharp

Pull requests to FSharp are welcome.

FSharp is only compatible with **Sublime Text 3**.


#### Building

### Linux/Mac

```shell
./build.sh
```

### Windows

```shell
build.cmd
```

The build target 'Install' will copy the built output into ST3's Packages directory:

```shell
./build.sh install
```

If you're running a portable install of Sublime Text you need to tell the build script where to install: 

```shell
./build.sh install sublimeDir="d:\AppData\ST3"
```

#### General steps

* Clone this repository to any folder outside of Sublime Text's *Data* folder
* Edit files as needed
* Install into Sublime Text: `./build.sh install`
* Restart Sublime Text
* Run the tests via command palette: *FSharp: Run Tests*
