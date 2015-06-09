#r "packages/FAKE/tools/FakeLib.dll" // include Fake lib
#r "System.Management"

open System
open System.Net
open System.IO
open System.Management
open Fake
open Fake.Git
open Fake.ProcessHelper

let releaseRepo = "https://github.com/guillermooo/sublime-fsharp-package-releases.git"

// build parameters
let dataDir     = getBuildParam "sublimeDir"

ProcessHelper.killCreatedProcesses <- false

let isWindows = (Path.DirectorySeparatorChar = '\\')
let sublimeDataPath () =
  let UnixPaths =
      [  (Environment.GetEnvironmentVariable("HOME") + "/Library/Application Support/Sublime Text 3")
         (Environment.GetEnvironmentVariable("HOME") + "/.config/sublime-text-3") ]

  let WindowsPaths =
    // Non-standard variable. It saves time while developing.
    [  Environment.GetEnvironmentVariable("SUBLIME_TEXT_DATA")
       Environment.ExpandEnvironmentVariables(@"%APPDATA%\Sublime Text 3") ]

  let searchPaths = if isWindows then WindowsPaths else UnixPaths
  let directories =
     searchPaths
     |> List.filter Directory.Exists

  match directories.Length with
  | 0 -> trace "No Sublime text 3 installation found"
         exit 1
  | _ -> directories.Head

let getSublimeStartArgs () =
    if not isWindows then
        let isRunning = getProcessesByName("Sublime Text") |> Seq.length > 0
        if isRunning then Some("open", "-a \"Sublime Text\"") else None
    else
        let query = "SELECT CommandLine FROM Win32_Process WHERE Name LIKE '%sublime_text%'"
        use searcher = new System.Management.ManagementObjectSearcher(query);
        searcher.Get ()
        |> Seq.cast
        |> Seq.tryFind (fun (mo:ManagementObject) -> true)
        |> Option.map (fun mo -> mo.["CommandLine"] |> string, "")

let startSublime (startArgs: (string*string) option) =
   startArgs |> Option.iter(fun (file,args) ->
     fireAndForget (fun info ->
       info.FileName <- file
       info.Arguments <- args
     )
   )

let killSublime () =
   let proc = if isWindows then "sublime_text" else "Sublime Text"
   killProcess proc

Target "Clean" (fun _ ->
    DeleteDirs ["bin"; "release"]
)

Target "Build" (fun _ ->
   CreateDir "bin"
   CopyRecursive "FSharp" "bin" true |> ignore
   Unzip "bin/fsac/fsac" "paket-files/github.com/packages/fsac"
)

Target "Install" (fun _ ->
    let startArgs = getSublimeStartArgs ()
    killSublime ()
    let sublimePath = if (not (String.IsNullOrWhiteSpace dataDir)) && (Directory.Exists dataDir) then dataDir else sublimeDataPath ()
    trace sublimePath
    let target = Path.Combine(sublimePath, "Packages/FSharp")
    CopyRecursive "bin" target true |> ignore
    startSublime startArgs
)

Target "Release" (fun _ ->
    let tag = getBuildParam "tag"
    if String.IsNullOrEmpty (tag) then
        failwith "please provide a tag as 'tag=x.x.x'"
    CreateDir "release"
    Repository.clone "release" releaseRepo "."
    Repository.fullclean "release"
    CopyRecursive "bin" "release" true |> ignore
    DeleteDirs ["release/tests"]
    DeleteFile "release/test_runner.py"
    StageAll "release"
    Commit "release" (sprintf "new version %s" tag)
    Branches.tag "release" tag
    Branches.push "release"
    Branches.pushTag "release" releaseRepo tag
    Branches.tag "." tag
    Branches.pushTag "." "origin" tag
)

"Clean"
    ==> "Build"

"Build"
    ==> "Install"

"Build"
    ==> "Release"

RunTargetOrDefault "Build"
