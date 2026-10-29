"""Generates the static Stremio addon in docs/ for a given public base URL.

Usage: python -I tools/build.py --base https://<host>/<path> [--out docs]

Every resource path below is the exact path the Xbox app requests
(Core/Addons/AddonRequestBuilder.BuildResourceUri). The subtitles request
carries extras built by AddonSubtitlePlayback.CreateRequestExtras, so each
title also gets a file named after those extras.
"""

import argparse
import json
import pathlib
import shutil

ADDON_ID = "qa.stremio-xbox.pd"
ID_PREFIX = ADDON_ID + "."
CATALOG_ID = "qa-pd"
SERIES_CATALOG_ID = "qa-pd-series"

# 80 minutes covers The General (78:52), Sintel (14:48) and Caminandes (2:30).
CUE_SPAN_SECONDS = 80 * 60
CUE_STEP_SECONDS = 5
CUE_LENGTH_MS = 4600

GENERAL = {
    "id": ID_PREFIX + "general1926",
    "name": "The General (1926) · QA 4:3",
    "releaseInfo": "1926",
    "runtime": "79 min",
    "poster": "https://archive.org/download/TheGeneral1926/__ia_thumb.jpg",
    "description": (
        "Buster Keaton and Clyde Bruckman, 1926. Public domain: archive.org item "
        "TheGeneral1926 (Public Domain Mark 1.0); a 1926 US publication. "
        "Xbox QA: 960x720 (4:3) direct MP4 with addon subtitles for the "
        "Y Fit / Crop / Stretch check."
    ),
}

SINTEL = {
    "id": ID_PREFIX + "sintel2010",
    "name": "Sintel (2010) · QA torrent",
    "releaseInfo": "2010",
    "runtime": "15 min",
    "poster": "https://webtorrent.io/torrents/Sintel/poster.jpg",
    "description": (
        "Sintel © copyright Blender Foundation | durian.blender.org, "
        "CC BY 3.0. WebTorrent's Sintel torrent (Sintel.mp4). Xbox QA: the "
        "addon subtitles below are menu candidates that load on demand, so "
        "LB walks subtitles that are not loaded yet."
    ),
}

GENERAL_STREAM = {
    "name": "QA direct",
    "title": "The General (1926) · archive.org 720p MP4 · 4:3",
    "url": "https://archive.org/download/TheGeneral1926/The_General_1926_720p.mp4",
    "behaviorHints": {
        "filename": "The_General_1926_720p.mp4",
        "videoSize": 1003361613,
    },
}

SINTEL_INFO_HASH = "08ada5a7a6183aae1e09d831df6748d566095a10"
SINTEL_STREAM = {
    "name": "QA torrent",
    "title": "Sintel (2010) · CC BY 3.0 · torrent, Sintel.mp4",
    "infoHash": SINTEL_INFO_HASH,
    "fileIdx": 5,
    "sources": [
        "tracker:udp://tracker.opentrackr.org:1337/announce",
        "tracker:udp://explodie.org:6969/announce",
        "tracker:udp://open.stealth.si:80/announce",
        "tracker:udp://tracker.torrent.eu.org:451/announce",
        "tracker:udp://open.demonii.com:1337/announce",
        "dht:" + SINTEL_INFO_HASH,
    ],
    "behaviorHints": {
        "filename": "Sintel.mp4",
        "videoSize": 129241752,
    },
}

# Caminandes, the Blender short series: three episodes of 1:30-2:30, each a
# direct 1080p H.264/AAC MP4 on archive.org. Video ids have no ':' because
# the app escapes it (%3A) and Pages would need a file named with ':', which
# a Windows checkout cannot hold. All episodes share one bingeGroup, so
# StremioAutoPlayStreamSelector picks the next episode's source.
CAMINANDES = {
    "id": ID_PREFIX + "caminandes",
    "name": "Caminandes · QA next episode",
    "releaseInfo": "2013-2016",
    "runtime": "2 min",
    "poster": "https://archive.org/download/CaminandesLlamigos/__ia_thumb.jpg",
    "description": (
        "Caminandes, the Blender short series about Koro the llama "
        "(Pablo Vazquez, Beorn Leonard, Francesco Siddi; music Jan "
        "Morgenstern; Blender Foundation, caminandes.com). Episodes 1 and 3 "
        "CC BY 3.0, episode 2 CC BY-SA 3.0. Xbox QA: three short episodes "
        "with one direct MP4 source each and one bingeGroup, for the "
        "next-episode popup and autoplay."
    ),
}
CAMINANDES_BINGE_GROUP = ADDON_ID + "|caminandes|archive.org-1080p-mp4"

# (episode, title, released, archive.org item, file name, size, overview)
CAMINANDES_EPISODES = [
    (1, "Llama Drama", "2013-02-09T00:00:00.000Z", "Caminandes1LlamaDrama",
     "01_llama_drama_1080p.mp4", 35103580,
     "Caminandes episode 1 (2013). 1:30, CC BY 3.0."),
    (2, "Gran Dillama", "2013-11-22T00:00:00.000Z", "Caminandes2GranDillama",
     "02_gran_dillama_1080p.mp4", 125974946,
     "Caminandes episode 2 (2013). 2:26, CC BY-SA 3.0."),
    (3, "Llamigos", "2016-01-29T00:00:00.000Z", "CaminandesLlamigos",
     "Caminandes_ Llamigos-1080p.mp4", 138945811,
     "Caminandes episode 3 (2016). 2:30, CC BY 3.0."),
]


def caminandes_video_id(episode):
    return f"{CAMINANDES['id']}.s1e{episode}"


def caminandes_videos():
    return [
        {
            "id": caminandes_video_id(episode),
            "title": title,
            "season": 1,
            "episode": episode,
            "released": released,
            "thumbnail": f"https://archive.org/download/{item}/__ia_thumb.jpg",
            "overview": overview,
        }
        for episode, title, released, item, _, _, overview in CAMINANDES_EPISODES
    ]


def caminandes_stream(episode, title, item, file, size):
    return {
        "name": "QA direct",
        "title": f"Caminandes S1E{episode} · {title} · archive.org 1080p MP4",
        "url": (f"https://archive.org/download/{item}/"
                + file.replace(" ", "%20")),
        "behaviorHints": {
            "bingeGroup": CAMINANDES_BINGE_GROUP,
            "filename": file,
            "videoSize": size,
        },
    }


# (file, BOM, language, label, first line, second line)
SUBTITLE_FILES = [
    ("qa-tr-bom.srt", True, "tur", "QA Türkçe (UTF-8 BOM)",
     "QA TR-BOM", "Türkçe deneme: ğüşıöç İĞÜŞÖÇ (UTF-8 BOM)"),
    ("qa-tr-nobom.srt", False, "tur", "QA Türkçe (UTF-8, BOM yok)",
     "QA TR-NOBOM", "Türkçe deneme: ğüşıöç İĞÜŞÖÇ (UTF-8, BOM yok)"),
    ("qa-en.srt", False, "eng", "QA English (UTF-8, no BOM)",
     "QA EN", "English test cue (UTF-8, no BOM)"),
]

# Listed for Sintel only and never generated: the load fails, so the app
# should mark it unavailable and LB should skip it.
MISSING_SUBTITLE = ("qa-missing.srt", "eng", "QA missing file (404)")


def timestamp(ms):
    hours, ms = divmod(ms, 3_600_000)
    minutes, ms = divmod(ms, 60_000)
    seconds, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"


def clock(seconds):
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def srt(tag, line2):
    blocks = []
    for number, start in enumerate(range(0, CUE_SPAN_SECONDS, CUE_STEP_SECONDS), 1):
        start_ms = start * 1000
        blocks.append(
            f"{number}\r\n"
            f"{timestamp(start_ms)} --> {timestamp(start_ms + CUE_LENGTH_MS)}\r\n"
            f"{tag} #{number:04} - {clock(start)}\r\n"
            f"{line2}\r\n")
    return "\r\n".join(blocks)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n")


def subtitle_entries(base, include_missing):
    entries = [
        {"id": file.removesuffix(".srt"), "lang": lang, "label": label,
         "url": f"{base}/subs/{file}"}
        for file, _, lang, label, _, _ in SUBTITLE_FILES
    ]
    if include_missing:
        file, lang, label = MISSING_SUBTITLE
        entries.append({"id": file.removesuffix(".srt"), "lang": lang,
                        "label": label, "url": f"{base}/subs/{file}"})
    return {"subtitles": entries}


def meta(title, kind="movie"):
    return {
        "id": title["id"],
        "type": kind,
        "name": title["name"],
        "poster": title["poster"],
        "background": title["poster"],
        "description": title["description"],
        "releaseInfo": title["releaseInfo"],
        "runtime": title["runtime"],
        "genres": ["QA"],
    }


def subtitle_extras_path(stream):
    # AddonSubtitlePlayback.CreateRequestExtras order: videoHash, videoSize,
    # filename. No stream has a videoHash. Pages decodes the request path,
    # so a space in the file name (%20 in the request) stays a space here.
    hints = stream["behaviorHints"]
    return f"videoSize={hints['videoSize']}&filename={hints['filename']}"


def write_subtitles(out, kind, video_id, stream, subtitles):
    write_json(out / "subtitles" / kind / f"{video_id}.json", subtitles)
    write_json(out / "subtitles" / kind / video_id /
               f"{subtitle_extras_path(stream)}.json", subtitles)


def build(base, out):
    base = base.rstrip("/")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / ".nojekyll").write_text("", encoding="utf-8")

    write_json(out / "manifest.json", {
        "id": ADDON_ID,
        "version": "1.1.0",
        "name": "Xbox QA (public domain)",
        "description": (
            "Temporary QA addon for the Stremio Xbox app: a 4:3 public-domain "
            "film and a CC BY torrent with self-written test subtitles "
            "(Turkish with and without BOM, English), plus the CC-licensed "
            "Caminandes short series for the next-episode checks. Not for "
            "general use."),
        "types": ["movie", "series"],
        "idPrefixes": [ID_PREFIX],
        "resources": ["catalog", "meta", "stream", "subtitles"],
        "catalogs": [
            {"type": "movie", "id": CATALOG_ID, "name": "Xbox QA"},
            {"type": "series", "id": SERIES_CATALOG_ID, "name": "Xbox QA"},
        ],
        "behaviorHints": {"configurable": False, "configurationRequired": False},
    })

    write_json(out / "catalog" / "movie" / f"{CATALOG_ID}.json",
               {"metas": [meta(GENERAL), meta(SINTEL)]})

    for title, stream, include_missing in (
            (GENERAL, GENERAL_STREAM, False),
            (SINTEL, SINTEL_STREAM, True)):
        write_json(out / "meta" / "movie" / f"{title['id']}.json",
                   {"meta": meta(title)})
        write_json(out / "stream" / "movie" / f"{title['id']}.json",
                   {"streams": [stream]})
        write_subtitles(out, "movie", title["id"], stream,
                        subtitle_entries(base, include_missing))

    write_json(out / "catalog" / "series" / f"{SERIES_CATALOG_ID}.json",
               {"metas": [meta(CAMINANDES, "series")]})
    write_json(out / "meta" / "series" / f"{CAMINANDES['id']}.json",
               {"meta": {**meta(CAMINANDES, "series"),
                         "videos": caminandes_videos()}})
    for episode, title, _, item, file, size, _ in CAMINANDES_EPISODES:
        video_id = caminandes_video_id(episode)
        stream = caminandes_stream(episode, title, item, file, size)
        write_json(out / "stream" / "series" / f"{video_id}.json",
                   {"streams": [stream]})
        write_subtitles(out, "series", video_id, stream,
                        subtitle_entries(base, include_missing=False))

    subs = out / "subs"
    subs.mkdir()
    for file, bom, _, _, tag, line2 in SUBTITLE_FILES:
        data = srt(tag, line2).encode("utf-8")
        (subs / file).write_bytes((b"\xef\xbb\xbf" if bom else b"") + data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--out", default=str(
        pathlib.Path(__file__).resolve().parent.parent / "docs"))
    args = parser.parse_args()
    build(args.base, pathlib.Path(args.out))


if __name__ == "__main__":
    main()
