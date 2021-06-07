# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import bpy, bmesh, math
from mathutils import Vector, Matrix
from numpy.linalg import solve
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, FloatProperty, EnumProperty


class ExportQuakeMap(bpy.types.Operator, ExportHelper):
    bl_idname = 'export.map'
    bl_label = "(Gtk/Net)Radiant Quake .map"
    bl_description = "Export scene as (Gtk/NetRadiant) Quake map"
    bl_options = {'UNDO'}
    filename_ext = ".map"
    filter_glob: StringProperty(default="*.map", options={'HIDDEN'})

    option_sel: BoolProperty(name="Selection only", default=True)
    option_tm: BoolProperty(name="Apply transform", default=True)
    option_grid: FloatProperty(name="Grid", default=4.0,
        description="Snap to grid (0 for off-grid)", min=0.0, max=256.0)
    option_format: EnumProperty(name="Format", default='Quake',
        items=( ('Quake', "Standard", "Axis-aligned texture projection"),
                ('Valve', "Valve220", "Face-bound texture projection") ) )
    option_dest: EnumProperty(name="Save to", default='File',
        items=( ('File', "File", "Write data to a .map file"),
                ('Clip', "Clipboard", "Store data in system buffer") ) )
    option_skip: StringProperty(name="Fallback", default='skip',
        description="Texture to use on new and unassigned faces")

    def gridsnap(self, vector):
        grid = self.option_grid
        if grid:
            return [round(co/grid)*grid for co in vector]
        else:
            return vector

    def printvec (self, vector):
        return ' '.join([f'{co:.5g}' for co in vector])

    def texdata(self, face, mesh, obj):
        mat = None
        width = height = 64
        if obj.material_slots:
            mat = obj.material_slots[face.material_index].material
        if mat:
            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE':
                    width, height = node.image.size
                    break
            texstring = mat.name
        else:
            texstring = self.option_skip

        V = [loop.vert.co for loop in face.loops]
        uv_layer = mesh.loops.layers.uv.active
        if uv_layer is None:
            uv_layer = mesh.loops.layers.uv.new("dummy")
        T = [loop[uv_layer].uv for loop in face.loops]

        # UV handling ported from: https://bitbucket.org/khreathor/obj-2-map

        if self.option_format == 'Valve':
            # [ Ux Uy Uz Uoffs ] [ Vx Vy Vz Voffs ] rotation scaleU scaleV
            dummy = ' [ 1 0 0 0 ] [ 0 -1 0 0 ] 0 1 1\n'

            height = -height # workaround for flipped v

            # Set up "2d world" coordinate system with the 01 edge along X
            world01 = V[1] - V[0]
            world02 = V[2] - V[0]

            if world01.length < 0.00001 or world02.length < 0.00001:
              world01_02Angle = 0
            else:
              world01_02Angle = world01.angle(world02)

            if face.normal.dot(world01.cross(world02)) < 0:
                world01_02Angle = -world01_02Angle
            world01_2d = Vector((world01.length, 0.0))
            world02_2d = Vector((math.cos(world01_02Angle),
                                math.sin(world01_02Angle))) * world02.length

            # Get 01 and 02 vectors in UV space and scale them
            tex01 = T[1] - T[0]
            tex02 = T[2] - T[0]
            tex01.x *= width
            tex02.x *= width
            tex01.y *= height
            tex02.y *= height

            '''
            a = world01_2d
            b = world02_2d
            p = tex01
            q = tex02

            [ px ]   [ m11 m12 0 ] [ ax ]
            [ py ] = [ m21 m22 0 ] [ ay ]
            [ 1  ]   [ 0   0   1 ] [ 1  ]

            [ qx ]   [ m11 m12 0 ] [ bx ]
            [ qy ] = [ m21 m22 0 ] [ by ]
            [ 1  ]   [ 0   0   1 ] [ 1  ]

            px = ax * m11 + ay * m12
            py = ax * m21 + ay * m22
            qx = bx * m11 + by * m12
            qy = bx * m21 + by * m22

            [ px ]   [ ax ay 0  0  ] [ m11 ]
            [ py ] = [ 0  0  ax ay ] [ m12 ]
            [ qx ]   [ bx by 0  0  ] [ m21 ]
            [ qy ]   [ 0  0  bx by ] [ m22 ]
            '''

            # Find an affine transformation to convert 
            # world01_2d and world02_2d to their respective UV coords
            texCoordsVec = Vector((tex01.x, tex01.y, tex02.x, tex02.y))
            world2DMatrix = Matrix(((world01_2d.x, world01_2d.y, 0, 0),
                                    (0, 0, world01_2d.x, world01_2d.y),
                                    (world02_2d.x, world02_2d.y, 0, 0),
                                    (0, 0, world02_2d.x, world02_2d.y)))
            try:
                mCoeffs = solve(world2DMatrix, texCoordsVec)
            except:
                return texstring + dummy
            right_2dworld = Vector(mCoeffs[0:2])
            up_2dworld = Vector(mCoeffs[2:4])

            # These are the final scale values
            # (avoid division by 0 for degenerate or missing UVs)
            scalex = 1 / max(0.00001, right_2dworld.length)
            scaley = 1 / max(0.00001, up_2dworld.length)
            scale = Vector((scalex, scaley))

            # Get the angles of the texture axes. These are in the 2d world
            # coordinate system, so they're relative to the 01 vector
            right_2dworld_angle = math.atan2(right_2dworld.y, right_2dworld.x)
            up_2dworld_angle = math.atan2(up_2dworld.y, up_2dworld.x)

            # Recreate the texture axes in 3d world coordinates,
            # using the angles from the 01 edge
            rt = world01.normalized()
            up = rt.copy()
            rt.rotate(Matrix.Rotation(right_2dworld_angle, 3, face.normal))
            up.rotate(Matrix.Rotation(up_2dworld_angle, 3, face.normal))

            # Now we just need the offsets
            rt_full = rt.to_4d()
            up_full = up.to_4d()
            test_s = V[0].dot(rt) / (width * scale.x)
            test_t = V[0].dot(up) / (height * scale.y)
            rt_full[3] = (T[0].x - test_s) * width
            up_full[3] = (T[0].y - test_t) * height

            texstring += f" [ {self.printvec(rt_full)} ]"\
                        f" [ {self.printvec(up_full)} ]"\
                        f" 0 {self.printvec(scale)}\n"

        elif self.option_format == 'Quake':
            # offsetU offsetV rotation scaleU scaleV
            dummy = ' 0 0 0 1 1\n'

            # 01 and 02 in 3D space
            world01 = V[1] - V[0]
            world02 = V[2] - V[0]

            # 01 and 02 projected along the closest axis
            maxn = max(abs(round(crd,5)) for crd in face.normal)
            for i in [2,0,1]: # axis priority for 45 degree angles
                if round(abs(face.normal[i]),5) == maxn:
                    axis = i
                    break
            world01_2d = Vector((world01[:axis] + world01[(axis+1):]))
            world02_2d = Vector((world02[:axis] + world02[(axis+1):]))

            # 01 and 02 in UV space (scaled to texture size)
            tex01 = T[1] - T[0]
            tex02 = T[2] - T[0]
            tex01.x *= width
            tex02.x *= width
            tex01.y *= height
            tex02.y *= height

            # Find affine transformation between 2D and UV
            texCoordsVec = Vector((tex01.x, tex01.y, tex02.x, tex02.y))
            world2DMatrix = Matrix(((world01_2d.x, world01_2d.y, 0, 0),
                                    (0, 0, world01_2d.x, world01_2d.y),
                                    (world02_2d.x, world02_2d.y, 0, 0),
                                    (0, 0, world02_2d.x, world02_2d.y)))
            try:
                mCoeffs = solve(world2DMatrix, texCoordsVec)
            except:
                return texstring + dummy

            # Build the transformation matrix and decompose it
            tformMtx = Matrix(( (mCoeffs[0], mCoeffs[1], 0),
                                (mCoeffs[2], mCoeffs[3], 0),
                                (0,          0,          1) ))
            t0 = Vector((T[0].x * width, T[0].y * height)).to_3d()
            v0 = Vector((V[0][:axis] + V[0][(axis+1):])).to_3d()

            offset = t0 - ( tformMtx @ v0 )
            rotation = math.degrees(tformMtx.inverted_safe().to_euler().z)
            scale = tformMtx.inverted_safe().to_scale() # always positive

            # Compare normals between UV and projection to get the scale sign
            tn = tex01.to_3d().cross(tex02.to_3d())
            vn = world01_2d.to_3d().cross(world02_2d.to_3d())
            if tn.dot(vn) < 0: scale.x *= -1

            # fudge
            offset.x += width
            offset.y *= -1

            finvals = [offset.x, offset.y, rotation, scale.x, scale.y]
            texstring += f" {self.printvec(finvals)}\n"

        return texstring

    def execute(self, context):
        if self.option_sel:
            objects = context.selected_objects
        else:
            objects = context.scene.objects
        non_entity_meshes = [obj for obj in objects if obj.type == 'MESH'
            and len(obj.blendradiant.entity_key_value_pairs) == 0]
        entity_meshes = [obj for obj in objects if obj.type == 'MESH'
            and len(obj.blendradiant.entity_key_value_pairs) > 0]

        geos = []

        # "non-entity" (= worldspawn entity, actually) brushes
        non_entity_key_value_pairs = { "classname": "worldspawn" }
        if self.option_format == 'Valve':
            non_entity_key_value_pairs["mapversion"] = "220"
        geo = self._write_entity(non_entity_meshes, non_entity_key_value_pairs)
        geos.append(geo)

        # entity brushes
        for obj in entity_meshes:
            entity_key_value_pairs = {
                "classname": obj.blendradiant.entity_classname
            }
            entity_key_value_pairs.update({
                pair.key: pair.value for pair
                in obj.blendradiant.entity_key_value_pairs
            })
            geo = self._write_entity([obj], entity_key_value_pairs)
            geos.append(geo)

        # put everything together and write out or store in clipboard
        map_file_contents = "\n".join(''.join(geo) for geo in geos if geo)
        if self.option_dest == 'File':
            with open(self.filepath, 'w') as file:
                file.write(map_file_contents)
        else:
            bpy.context.window_manager.clipboard = map_file_contents

        return {'FINISHED'}

    # TODO it's bad style to have fw as an argument here; better to use
    # separate lists
    def _write_entity(self, objects, key_value_pairs):
        geo = []
        fw = geo.append

        fw('{\n')
        fw("\n".join([f'"{k}" "{v}"' for k, v in key_value_pairs.items()]))
        fw('\n')

        # store active + selected objects in editor because
        # we will have to change them to apply high-level op
        prev_active = bpy.context.view_layer.objects.active
        prev_selected = list(bpy.context.view_layer.objects.selected)

        for top_level_obj in objects:
            # subdivide mesh into "room brushes" if requested
            if top_level_obj.blendradiant.mesh_as == "CONVEX_BRUSH":
                sub_objs = [top_level_obj]
            elif top_level_obj.blendradiant.mesh_as == "ROOM_BRUSHES":
                # deep copying objects code from:
                # https://blender.stackexchange.com/a/135608/114640
                tmp_obj = top_level_obj.copy()
                tmp_obj.data = top_level_obj.data.copy()
                # link to scene so we'll be able to use it
                bpy.context.collection.objects.link(tmp_obj)
                # select copy (context override didn't work...)
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = tmp_obj
                tmp_obj.select_set(True)
                # apply make_room operator to copy
                thickness = top_level_obj.blendradiant.room_brush_thickness
                bpy.ops.mesh.make_room(thickness=thickness)
                # these are the room brush objects
                sub_objs = list(bpy.context.view_layer.objects.selected)
            else:
                sub_objs = []

            for obj in sub_objs:
                bm = bmesh.new()
                bm.from_mesh(obj.data)
                if self.option_tm:
                    bmesh.ops.transform(bm, matrix=obj.matrix_world,
                                                    verts=bm.verts)
                for vert in bm.verts:
                    vert.co = self.gridsnap(vert.co)
                hull = bmesh.ops.convex_hull(bm, input=bm.verts,
                                        use_existing_faces=True)
                geom = hull['geom'] + hull['geom_holes']
                oldfaces = [face for face in bm.faces if face not in geom]
                bmesh.ops.delete(bm, geom=oldfaces, context='FACES')
                bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
                bmesh.ops.join_triangles(bm, faces=bm.faces,
                    angle_face_threshold=0.01, angle_shape_threshold=0.7)
                bmesh.ops.connect_verts_nonplanar(bm, faces=bm.faces,
                                                    angle_limit=0.0)
                fw('{\n')
                for face in bm.faces:
                    for vert in reversed(face.verts[0:3]):
                        fw(f'( {self.printvec(vert.co)} ) ')
                    fw(self.texdata(face, bm, obj))
                fw('}\n')
                bm.clear()

                bm.free()

                # only delete this if it's composed of tmp objects for room brushes!
                if top_level_obj.blendradiant.mesh_as == "ROOM_BRUSHES":
                    bpy.data.objects.remove(obj)

        # we don't have to remove tmp_obj as it went into
        # the first sub_obj during make_room!

        # restore previous active + selected
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = prev_active
        for _prev_selected in prev_selected:
                _prev_selected.select_set(True)


        fw('}')

        return geo


def menu_func_export(self, context):
    self.layout.operator(ExportQuakeMap.bl_idname, text="(Gtk/NetRadiant) Quake Map (.map)")
