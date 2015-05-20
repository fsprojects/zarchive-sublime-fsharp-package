#r "packages/FAKE/tools/FakeLib.dll" // include Fake lib

open System
open System.Net
open System.IO
open Fake
open Fake.ProcessHelper

// build parameters
let installDir     = getBuildParam "sublimeDir"
let restartSublime = getBuildParam "restartSublime" |> String.IsNullOrWhiteSpace |> not

ProcessHelper.killCreatedProcesses <- false

let isWindows = (Path.DirectorySeparatorChar = '\\')
let sublimePath () =
  let UnixPaths =
      [ (Environment.GetEnvironmentVariable("HOME") + "/Library/Application Support/Sublime Text 3")
        (Environment.GetEnvironmentVariable("HOME") + "/.config/sublime-text-3") ]

  let WindowsPaths =
      [ Environment.ExpandEnvironmentVariables(@"%APPDATA%\Sublime Text 3") ]

  let searchPaths = if isWindows then WindowsPaths else UnixPaths
  let directories =
     searchPaths
     |> List.filter Directory.Exists

  match directories.Length with
  | 0 -> trace "No Sublime text 3 installation found"
         exit 1
  | _ -> directories.Head

let startSublime () =
   trace "Starting sublime"
   fireAndForget (fun info ->
     info.FileName <- "open"
     info.Arguments <- "-a \"Sublime Text\""
   )

Target "KillSublime" (fun _ ->
   let proc = if isWindows then "sublime_text" else "Sublime Text"
   killProcess proc
)

Target "Clean" (fun _ ->
   DeleteDirs ["bin"]
)

Target "Build" (fun _ ->
   CreateDir "bin"
   CopyRecursive "FSharp" "bin" true |> ignore
   Unzip "bin/fsac/fsac" "paket-files/github.com/packages/fsac"
)

Target "Install" (fun _ ->
   let sublimePath = if (not (String.IsNullOrWhiteSpace installDir)) && (Directory.Exists installDir) then installDir else sublimePath ()
   trace sublimePath
   let target = Path.Combine(sublimePath, "Packages/FSharp")
   CopyRecursive "bin" target true |> ignore
   trace "fdkmgmkd"
   if restartSublime then do startSublime ()
)

"Clean"
   =?> ("KillSublime", restartSublime)
   ==> "Build"
   ==> "Install"

RunTargetOrDefault "Build"
