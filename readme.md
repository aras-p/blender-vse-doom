# Doom running in Blender Video Sequence Editor timeline

Here's a video! <br/>
[![Doom in Blender VSE timeline](https://img.youtube.com/vi/Y2iDZjteMs8/0.jpg)](https://www.youtube.com/watch?v=Y2iDZjteMs8)

A modal blender operator that loads doom file, creates
VSE timeline full of color strips (80 columns, 60 rows), listens to
keyboard input for player control, renders doom frame and updates the
VSE color strip colors to match the rendered result. Escape key finishes
the operator.

> I have no idea what I'm doing, so it is entirely possible that the
> operator is written in a completely nonsensical way!

All the Doom-specific heavy lifting is in `render.py`, written by
Mark Dufour and is completely unrelated to Blender. It is just a tiny
pure Python Doom loader/renderer. I took it from
"[Minimal DOOM WAD renderer](https://github.com/shedskin/shedskin/blob/6c30bbe617/examples/doom/render.py)"
and made two small edits to avoid division by zero exceptions that I was getting.


## Instructions

1. Download code of this repository.
1. Put `doom1.wad` next to `vse_doom.blend` file, can get it from [doomwiki](https://doomwiki.org/wiki/DOOM1.WAD)
   or other places.
1. Open `vse_doom.blend` file in Blender. The file is made with Blender 4.0, I have tested up to Blender 4.4.
1. Click "Run Script" atop of the script editor window.
1. This will create 80x60 color strips in the VSE timeline below, load E1M1 from `doom1.wad` and start a modal operator
   that reacts to arrow keys to move. Escape finishes the operator and returns to "normal blender".


## Performance

This runs pretty slow (~3fps) currently (blender 4.1-4.4), due to various VSE shenanigans. Updating colors of
almost 5000 color strips is slow, it turns out.

The pure-python Doom renderer, while perhaps written in not performant Python way, is not the slow part here.
It takes about 7 milliseconds to render 80x60 frame. It takes almost 300 milliseconds to update the colors
of all the VSE strips, in comparison. I will see if I can optimize it somehow!

In Blender 4.0 or earlier it runs even slower, because redrawing the VSE timeline with 5000 strips
takes about 100 milliseconds; that is no longer slow in 4.1+ (1-2ms).


## .blend file contents

The `vse_doom.blend` file itself contains pretty much nothing, except this text script block:

```
import bpy
import os
import sys

# add blend file folder to import path, so that we can use .py scripts next to the file
blen_dir = os.path.normpath(os.path.join(__file__, "..", ".."))
if blen_dir not in sys.path:
    sys.path.append(blen_dir)

# make sure to reload run_doom/render modules so we can do edits while blender is running
if "run_doom" in sys.modules:
    del sys.modules["run_doom"]
if "render" in sys.modules:
    del sys.modules["render"]

import run_doom

def register():    
    try:
        bpy.utils.register_class(run_doom.DoomOperator)
    except:
        pass # was already registered

def unregister():
    bpy.utils.unregister_class(run_doom.DoomOperator)

if __name__ == "__main__":
    register()
    bpy.ops.lol.doom_player('INVOKE_DEFAULT')
```