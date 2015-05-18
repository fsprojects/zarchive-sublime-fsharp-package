#r "packages/FAKE/tools/FakeLib.dll" // include Fake lib
#r @"System.IO.Compression"
#r @"System.IO.Compression.FileSystem"

open System
open System.Net
open System.IO
open System.IO.Compression
open Fake 

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
    DeleteDirs ["bin"]
)

Target "Build" (fun _ ->
    CreateDir "bin"
    CopyRecursive "FSharp" "bin" true |> ignore
    Unzip "bin/fsac/fsac" "paket-files/github.com/packages/fsac"
)

Target "Install" (fun _ ->
    let installDir = getBuildParam "sublimeDir"
    let sublimePath = if (not  (String.IsNullOrWhiteSpace installDir)) && (Directory.Exists installDir) then installDir else sublimePath ()
    trace sublimePath
    let target = Path.Combine(sublimePath, "Packages/FSharp")
    CopyRecursive "bin" target true |> ignore
)

"Clean" 
   ==> "Build"
   ==> "Install"

RunTargetOrDefault "Build"