# https://github.com/shedskin/shedskin/blob/master/examples/doom/doom.py

import bpy
import os
import math
import time

import render

class DoomOperator(bpy.types.Operator):
    bl_idname = "lol.doom_player"
    bl_label = "Doom Player"
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timer = None
        self.strip_lookup = None
        self.map = None
        self.blender_palette = None
        self.player = None
        
    def create_strips(self):
        bpy.context.scene.sequence_editor_clear()
        if not bpy.context.scene.sequence_editor:
            bpy.context.scene.sequence_editor_create()

        width = render.WIDTH
        height = render.HEIGHT
        dur = 10
        self.strip_lookup = [None] * (width * height)
        
        for y in range(height):
            for x in range(width):
                start = x * dur + 1
                strip = bpy.context.scene.sequence_editor.sequences.new_effect(
                    name=f"C{x}_{y}",
                    type='COLOR',
                    channel=y + 1,
                    frame_start=start,
                    frame_end=start + dur - 1
                )
                strip.select = False
                idx = (height - 1 - y) * width + x
                self.strip_lookup[idx] = strip
        bpy.context.scene.frame_end = width * dur
                
        
    def update_strips(self, data):
        num = len(data)
        for idx in range(num):
            val = data[idx]
            col = self.blender_palette[val]
            self.strip_lookup[idx].color = col
    
    def modal(self, context, event):
        # Escape stops
        if event.type == 'ESC':
            context.window_manager.event_timer_remove(self.timer)
            context.window.cursor_modal_restore()
            return {'FINISHED'}
        
        if event.type == 'TIMER':
            self.frame_update()
        elif event.type == 'LEFT_ARROW' and event.value == 'PRESS':
            self.player.angle += math.radians(20)
        elif event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
            self.player.angle -= math.radians(20)
        elif event.type == 'UP_ARROW' and event.value == 'PRESS':
            self.move_player(7.0, 0)            
        elif event.type == 'DOWN_ARROW' and event.value == 'PRESS':
            self.move_player(-7.0, 0)
        
        return {'RUNNING_MODAL'}
    
    def move_player(self, dist, strafe):
        dx = dist * math.cos(self.player.angle + strafe)
        dy = dist * math.sin(self.player.angle + strafe)
        self.player.x += dx
        self.player.y += dy

    def invoke(self, context, event):
        context.window.cursor_modal_set('HAND')
        
        # create strips
        t0 = time.perf_counter()
        self.create_strips()
        t1 = time.perf_counter()
        print(f"doom: created {render.WIDTH}x{render.HEIGHT} ({render.WIDTH*render.HEIGHT}) strips in {(t1-t0)*1000:.1f}ms")
        self.frame_count = 0
        
        # load doom map
        blen_dir = os.path.normpath(os.path.join(__file__, ".."))
        mapname = 'E1M1'
        t0 = time.perf_counter()
        self.map = render.Map(f"{blen_dir}/doom1.wad", mapname)
        t1 = time.perf_counter()
        print(f"doom: loaded {mapname} in {(t1-t0)*1000:.1f}ms")
        palette = self.map.palette
        self.blender_palette = [(r/255, g/255, b/255) for r,g,b in palette]
        self.player = self.map.player
        
        wm = context.window_manager
        self.timer = wm.event_timer_add(0.1, window=context.window)                
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def frame_update(self):
        
        # update player
        pl = self.player        
        pl.z = pl.floor_h + 48
        pl.update()
        
        # render frame and update strip colors

        t0 = time.perf_counter()
        buf = render.render(self.map, self.frame_count)
        t1 = time.perf_counter()
        self.update_strips(buf)
        t2 = time.perf_counter()
        if self.frame_count % 8 == 0:
            print(f"doom: render {(t1-t0)*1000:.1f}ms strip color update {(t2-t1)*1000:.1f}ms")

        self.frame_count += 1
