# v1.1.0 live verification — October 2, 2026 (Pacific)

**Release status: blocked by hosted MCP argument validation.**

These are authenticated production MCP calls using a temporary Python MCP
client, the published tool schemas, and the v1.1.0 workflow instructions.
They are not a clean-install Codex conversation test or proof that Codex will
select every workflow correctly. Raw account results and media links remain
local; no tokens, reviewer credentials, or signed result links are committed.

## Results against the manager plan

| Feature | Observed result |
| --- | --- |
| Subtitle review before dubbing | Tool is enabled and starts a task. The public demo has no speech; it correctly returned `TRANSCRIPTION_EMPTY`. Successful subtitle generation and approved-script dubbing remain untested. |
| Music and effects together | Passed: one call produced a video, music track, and effects track. All three URLs were readable; video contains H.264 and AAC and is 20 seconds long. |
| Free dubbing preview | Blocked: the documented `languages` string is rejected by argument validation before task creation. The account still has its preview allowance. |
| Full video after preview | Blocked by the same language-argument issue; no preview/full-video chain completed. |
| Balance and trial lookup | Passed: actual decimal USD balance and per-service trial data returned through OAuth. |
| Credit-error guidance | Guide routes were verified previously; an actual insufficient-balance rejection and Codex's reply are not yet tested. Do not exhaust the test wallet just to force this condition. |
| Continue after account update | Not tested: no account-funding change was performed. |
| Usage examples | Bundled examples are present; selection and wording in a clean Codex session remain untested. |
| Generation status | Passed: existing successful and failed tasks retrieved; repeat lookup returned the same task and media URLs. A nonexistent task returned `Task not found`. |
| Multiple variants | Passed: one 10-second request with `variants_num=3` returned three distinct playable audio files. |
| Keep narration audible | Not tested: the available public demo has no speech. Requires a spoken-video fixture. |
| Timed sound effects | Blocked: the documented `segments` JSON string is rejected before task creation. |
| Instrument stems | Passed: all three variants returned drums, bass, vocals, and other tracks; all 12 stem URLs were readable. |

Media verification used ffprobe for actual file readability, codecs, and duration.
It does not establish subjective audio quality or speech intelligibility.

## Confirmed hosted blocker

Both calls use the types advertised by production `tools/list`:

```json
{"languages": "[\"en\"]"}
```

```json
{"segments": "[{\"start\":0,\"end\":2,\"prompt\":\"Silence\"},{\"start\":2,\"end\":3,\"prompt\":\"Footstep\"}]"}
```

Production reports `Input should be a valid string`, with `input_type=list`.
FastMCP 1.14.1 reproduces the cause locally: `pre_parse_json` decodes JSON
strings when the annotation is `str | None`, then the argument model rejects
the resulting list. Calling the Python tool function directly does not exercise
this preprocessing, so earlier function-level checks missed it.

Fix the hosted argument model/normalization and add a regression test through
FastMCP dispatch. Audit other JSON-array string fields, including segments on
music/SFX/combined tools. Then retest the live language and timed-effect paths;
update plugin guidance if the published schema changes. Do not work around the
failure by omitting requested languages, which would select multiple defaults.

## OAuth test-client incident

The first temporary connection expired after waiting for authorization. On a
subsequent attempt, the callback completed but the Python client rejected the
token response because Clerk included `offline_access` in addition to `profile`.
The test client was restarted with both scopes explicitly requested, allowing
normal scope validation to remain enabled. Authenticated calls then succeeded.
Tokens are held only in the temporary client's memory.

The plugin manifest remains `profile` only. This temporary client's success
therefore does not establish the exact Codex client's sign-in/refresh behavior;
a clean plugin OAuth check is still required before release.

## Usage reconciliation

The live run recorded three generation requests, including the no-speech
failure, and USD 0.0675 spending. The wallet decreased by that same amount.
The combined-video trial was consumed; dubbing and timed-SFX trials were not.
No account funding or automatic paid retry was performed.

Still needed: fix and deploy hosted array-argument handling, a permitted public
spoken-video fixture, the remaining scenarios above, a clean v1.1.0 Codex
conversation test, the updated portal upload/scan, and current demo material.
