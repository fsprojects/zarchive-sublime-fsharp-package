#r "packages/FAKE/tools/FakeLib.dll" // include Fake lib

open System
open System.Net
open System.IO
open Fake
open Fake.Git

let sublimePath () =
  let UnixPaths =
      [  (Environment.GetEnvironmentVariable("HOME") + "/Library/Application Support/Sublime Text 3")
         (Environment.GetEnvironmentVariable("HOME") + "/.config/sublime-text-3") ]

  let WindowsPaths =
      [ Environment.ExpandEnvironmentVariables(@"%APPDATA%\Sublime Text 3") ]

  let isWindows = (Path.DirectorySeparatorChar = '\\')
  let searchPaths = if isWindows then WindowsPaths else UnixPaths
  let directories =
     searchPaths
     |> List.filter Directory.Exists

  match directories.Length with
     | 0 ->
         trace "No Sublime text 3 installation found"
         exit 1
     | _ ->
         directories.Head

Target "Clean" (fun _ ->
    DeleteDirs ["bin"; "release"]
)

Target "Build" (fun _ ->
    CreateDir "bin"
    CopyRecursive "FSharp" "bin" true |> ignore
    Unzip "bin/fsac/fsac" "paket-files/github.com/packages/fsac"
)

Target "Install" (fun _ ->
    let installDir = getBuildParam "sublimeDir"
    let sublimePath = if (not (String.IsNullOrWhiteSpace installDir)) && (Directory.Exists installDir) then installDir else sublimePath ()
    trace sublimePath
    let target = Path.Combine(sublimePath, "Packages/FSharp")
    CopyRecursive "bin" target true |> ignore
)

Target "Release" (fun _ ->
    let tag = getBuildParam "tag"
    CreateDir "release"
    Repository.clone "release" "https://github.com/guillermooo/sublime-fsharp-package-releases.git" "."
    Repository.fullclean "release"
    CopyRecursive "bin" "release" true |> ignore
    DeleteDirs ["release/tests"]
    DeleteFile "release/test_runner.py"
    // CommandHelper.gitCommand "release" "add --all ."
    // CommandHelper.gitCommand "release" "commit -m " (sprintf "\"new version %s\"" tag)
    // CommandHelper.gitCommand "release" ("tag " + tag)
    // CommandHelper.gitCommand "release" "push origin master --tags"
)

"Clean"
    ==> "Build"

"Build"
    ==> "Install"

"Build"
    ==> "Release"

RunTargetOrDefault "Build"
