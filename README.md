# Xbox QA test addon (public domain)

A small static [Stremio addon](https://github.com/Stremio/stremio-addon-sdk/blob/master/docs/protocol.md)
used for device QA of a Stremio client on Xbox. It is temporary and not meant
for general use.

Install URL (GitHub Pages):

```
https://mehmetcansahin.github.io/stremio-xbox-qa-addon/manifest.json
```

## What it serves

Two catalogs named **Xbox QA**: one for movies (`movie/qa-pd`, two movies)
and one for series (`series/qa-pd-series`, one series). Every id starts with
`qa.stremio-xbox.pd.`, so the addon never answers for Cinemeta (`tt…`) titles.

| Title | Stream | Why |
| --- | --- | --- |
| The General (1926) · QA 4:3 | Direct MP4 from archive.org, 960x720 (4:3) | Video scale Fit / Crop / Stretch with subtitles on |
| Sintel (2010) · QA torrent | WebTorrent's Sintel torrent, `Sintel.mp4` (fileIdx 5) | Addon subtitles that load only when chosen |
| Caminandes · QA next episode (series) | One direct 1080p MP4 per episode from archive.org | Next-episode popup and autoplay |

The series `qa.stremio-xbox.pd.caminandes` has three episodes in season 1.
Video ids use no `:` (the client escapes it, and a Windows checkout cannot
hold such a file name). Every episode's stream has the same
`behaviorHints.bingeGroup` (`qa.stremio-xbox.pd|caminandes|archive.org-1080p-mp4`),
so the client's autoplay picks the next episode's stream.

| Video id | Episode | Length | File (archive.org) |
| --- | --- | --- | --- |
| `qa.stremio-xbox.pd.caminandes.s1e1` | S1E1 Llama Drama (2013) | 1:30 | `Caminandes1LlamaDrama/01_llama_drama_1080p.mp4`, 35 MB |
| `qa.stremio-xbox.pd.caminandes.s1e2` | S1E2 Gran Dillama (2013) | 2:26 | `Caminandes2GranDillama/02_gran_dillama_1080p.mp4`, 126 MB |
| `qa.stremio-xbox.pd.caminandes.s1e3` | S1E3 Llamigos (2016) | 2:30 | `CaminandesLlamigos/Caminandes_ Llamigos-1080p.mp4`, 139 MB |

All files are 1920x1080 H.264 (High) with AAC audio.

Every title gets the same addon subtitles:

| Label | Language | Encoding |
| --- | --- | --- |
| QA Türkçe (UTF-8 BOM) | `tur` | UTF-8 with BOM |
| QA Türkçe (UTF-8, BOM yok) | `tur` | UTF-8 without BOM |
| QA English (UTF-8, no BOM) | `eng` | UTF-8 without BOM, ASCII only |
| QA missing file (404), Sintel only | `eng` | Not published on purpose: the load fails |

Each file has a cue every 5 seconds for 80 minutes. A cue shows its file tag,
its number and its start time (for example `QA TR-BOM #0013 - 00:01:00`), so a
screenshot tells which file is on screen.

## Sources and licenses

- **The General (1926)**, Buster Keaton and Clyde Bruckman. Public domain: a
  1926 US publication, and the archive.org item
  [TheGeneral1926](https://archive.org/details/TheGeneral1926) is marked
  [Public Domain Mark 1.0](http://creativecommons.org/publicdomain/mark/1.0/).
  The video is linked, not copied.
- **Sintel (2010)**, © copyright Blender Foundation | durian.blender.org,
  [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/). The stream is the
  public WebTorrent demo torrent (infohash
  `08ada5a7a6183aae1e09d831df6748d566095a10`); the poster is linked from
  webtorrent.io. Nothing from the film is copied here.
- **Caminandes**, a short series by Pablo Vazquez, Beorn Leonard and
  Francesco Siddi, music and sound by Jan Morgenstern, Blender Foundation /
  caminandes.com. The videos and the thumbnails are linked from archive.org,
  not copied.
  - S1E1 *Llama Drama* (2013):
    [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/). The archive.org
    item [Caminandes1LlamaDrama](https://archive.org/details/Caminandes1LlamaDrama)
    is marked CC BY 3.0, and so is the Wikimedia Commons copy
    [Caminandes- Llama Drama - Short Movie.ogv](https://commons.wikimedia.org/wiki/File:Caminandes-_Llama_Drama_-_Short_Movie.ogv).
  - S1E2 *Gran Dillama* (2013):
    [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). The
    archive.org item [Caminandes2GranDillama](https://archive.org/details/Caminandes2GranDillama)
    is marked CC BY 3.0, but the Wikimedia Commons copy
    [Caminandes - Gran Dillama](https://commons.wikimedia.org/wiki/File:Caminandes_-_Gran_Dillama_-_Blender_Foundation%27s_new_Open_Movie.webm)
    was license-reviewed as CC BY-SA 3.0 against caminandes.com, and the
    Commons page of
    [another copy](https://commons.wikimedia.org/wiki/File:Caminandes,_Gran_Dillama_-_Blender_Foundation.webm)
    notes that the film shows CC BY-SA 3.0 at 2:21. This addon follows the
    stricter CC BY-SA 3.0.
  - S1E3 *Llamigos* (2016):
    [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/). The archive.org
    item [CaminandesLlamigos](https://archive.org/details/CaminandesLlamigos)
    is marked CC BY 3.0, as is the Wikimedia Commons copy
    [Caminandes 3 - Llamigos](https://commons.wikimedia.org/wiki/File:Caminandes_3_-_Llamigos_-_Blender_Animated_Short.webm);
    Blender's own video site lists it as
    [Attribution](https://video.blender.org/videos/watch/23f3ef79-15dc-44c5-aa45-cf92e78a4509).
- **Subtitles**: written for this test (test labels and counters, no film
  dialogue). Dedicated to the public domain under
  [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).

## Building

`docs/` is generated; GitHub Pages serves it as the site root.

```
python -I tools/build.py --base https://mehmetcansahin.github.io/stremio-xbox-qa-addon
```

The subtitles request of the Xbox client carries `videoSize` and `filename`
extras, so each title (each episode, for the series) also has
`subtitles/<type>/<id>/videoSize=<bytes>&filename=<name>.json`.

## Uninstall

Remove "Xbox QA (public domain)" from the installed addons. The addon list is
synced to the Stremio account, so removing it once removes it everywhere.
