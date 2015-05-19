## FSharp - F# Coding Tools for Sublime Text

This package provides support
for F# development in Sublime Text.

**FSharp is currently a preview
and not ready for use**.
If you want to contribute to its development,
you can read on
to learn how to set up
a development environment.


### Developing FSharp

Pull requests to FSharp are welcome.

FSharp is only compatible
with **Sublime Text 3**.


#### Building

### Linux/Mac

```shell
./build.sh
```

### Windows

```shell
build.cmd
```

The **Install** build target
will publish the package
to Sublime Text's *Data* directory:

```shell
./build.sh install
```

For portable installations of Sublime Text
(Windows only),
you must pass along
the target directory:

```shell
build install sublimeDir="d:\Path\To\Sublime\Text\Data"
```

#### General steps

* Clone this repository to any folder outside of Sublime Text's *Data* folder
* Edit files as needed
* Install into Sublime Text: `./build.sh install`
* Restart Sublime Text
* Run the tests via command palette: *FSharp: Run Tests*
