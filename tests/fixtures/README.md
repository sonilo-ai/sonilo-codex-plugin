# Live-test media

`speech-demo.mp4` is a 22-second test card with locally synthesized English
narration. Its exact script is `speech-demo.txt`. It contains no customer media,
private account data, recorded person, or cloned voice.

Use this fixture for subtitle translation, 15-second preview/full-video
continuation, and speech-preserving soundtrack checks. Keep `lipsync=false`:
the image is a static test card with no visible speaker. These files are test
inputs outside `plugins/sonilo` and are not included in either release ZIP.

The initial file was generated with macOS `say -r 145` and FFmpeg, using H.264
video at 640x360/25 fps and AAC audio. The last seconds leave room for music to
return after speech. This is a diagnostic fixture, not a product-quality demo.
