# Xbox QA test addon (public domain)

A small static [Stremio addon](https://github.com/Stremio/stremio-addon-sdk/blob/master/docs/protocol.md)
used for device QA of a Stremio client on Xbox. It is temporary and not meant
for general use.

Install URL (GitHub Pages):

```
https://mehmetcansahin.github.io/stremio-xbox-qa-addon/manifest.json
```

## What it serves

One catalog, **Xbox QA**, with two movies. Every id starts with
`qa.stremio-xbox.pd.`, so the addon never answers for Cinemeta (`tt…`) titles.

| Title | Stream | Why |
| --- | --- | --- |
| The General (1926) · QA 4:3 | Direct MP4 from archive.org, 960x720 (4:3) | Video scale Fit / Crop / Stretch with subtitles on |
| Sintel (2010) · QA torrent | WebTorrent's Sintel torrent, `Sintel.mp4` (fileIdx 5) | Addon subtitles that load only when chosen |

Both titles get the same addon subtitles:

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
- **Subtitles**: written for this test (test labels and counters, no film
  dialogue). Dedicated to the public domain under
  [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).

## Building

`docs/` is generated; GitHub Pages serves it as the site root.

```
python -I tools/build.py --base https://mehmetcansahin.github.io/stremio-xbox-qa-addon
```

The subtitles request of the Xbox client carries `videoSize` and `filename`
extras, so each title also has
`subtitles/movie/<id>/videoSize=<bytes>&filename=<name>.json`.

## Uninstall

Remove "Xbox QA (public domain)" from the installed addons. The addon list is
synced to the Stremio account, so removing it once removes it everywhere.
