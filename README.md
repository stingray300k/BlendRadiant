# BlendRadiant

This is a fork of [c-d-a](https://github.com/c-d-a)'s `io_export_qmap` Blender
Addon, with the aim of modifying it until it can export maps that are directly
readable by (Gtk/Net)Radiant. Another aim is to add tools that facilitate the
creation of entire maps (including lights, models, entities, ... and not just
brushes) in Blender, basically allowing users to do everything they could
otherwise do in (Gtk/Net)Radiant - hence the name *BlendRadiant*.

## Status

Right now, only the UI has been worked on, while the actual export
functionality has only had features *removed* compared to `io_export_qmap`. I
only put this on GitHub to have an issue tracker.

![BlendRadiant object properties in Blender UI](https://user-images.githubusercontent.com/85426069/120913605-7b3f3280-c698-11eb-9687-7a34494cd6aa.png)

### Required features until "minimal viability"

- [x] Export meshes as "rooms" ("Make Room" in (Gtk/Net)Radiant)
- [ ] Export entity key-value pairs
  - [x] Read entity definitions from Radiant gamepack files
  - [x] UI for setting entity classname and attributes
  - [ ] Actual export
- [ ] Export lights
  - [ ] Special UI that is more limited version of entity UI
- [ ] Either output directly as Brush Primitive map (Radiant format) or use
      `q3map2` to convert after export
- [ ] Fix texture issues
- [ ] Massive cleanup

### Features that would be nice to have

- [ ] Global scale factor
- [ ] Export as models
- [ ] Read shader definitions (existing addons?)
  - [ ] Alternatively: export rudimentary shader based on Blender material as
        placeholder
- [ ] Scale mesh with point entity class so bounding box matches spec


Below is `io_export_qmap`'s original README:

-----

Exports either individual faces as pyramids, or objects as convex brushes. Uses material names for texture assignment and material image size for scaling. Supports UVs both in standard Quake and in Valve220 format (adapted from EricW's implementation for [OBJ2MAP](https://bitbucket.org/khreathor/obj-2-map)). Offers custom grid. Allows saving to clipboard.

The exporter ensures that the brushes are convex and the faces planar. You don't have to triangulate the meshes in advance, but in some cases it can help with UVs (e.g. with mid-edge vertices). There's room for improvement, but it should work fine as is.

Standard format UV export is lossy (no shearing). I don't really expect anyone to be using it over Valve220 anyway, but it should produce decent results for id1-style detailing. Single-axis curves should be fine, no miracles though.

Only tested in Trenchbroom for now. Might need to change precision for other editors. Let me know if it works/breaks elsewhere.
