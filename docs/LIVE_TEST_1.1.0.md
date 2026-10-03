# v1.1.0 verification — October 2–3, 2026 (Pacific)

**Release status: hosted fix deployed; remaining workflow and conversation checks.**

Backend [PR #393](https://github.com/sonilo-ai/sonilo-api-dashboard/pull/393)
fixes the six affected optional JSON-array string arguments without changing
their published schemas. After synchronizing the October 3 `develop` updates,
all 255 relevant local tests and the synchronized commit's CI passed. The PR
was merged as `946115c3` and deployed in
[production run 37143426954](https://github.com/sonilo-ai/sonilo-api-dashboard/actions/runs/37143426954).
ECS revision 95 reached COMPLETED with one running task and no pending tasks;
its image tag matches the merge commit. The updated plugin Skill upload also
passed the portal scanner; this is not approval or publication of the plugin.

These are authenticated production MCP calls using a temporary Python MCP
client, the published tool schemas, and the v1.1.0 workflow instructions.
They are not a clean-install Codex conversation test or proof that Codex will
select every workflow correctly. Raw account results and media links remain
local; no tokens, reviewer credentials, or signed result links are committed.

## Results against the manager plan

| Feature | Observed result |
| --- | --- |
| Subtitle review before dubbing | Subtitle generation passed on the synthetic spoken fixture: six English cues and their Spanish translations were returned, downloaded, and reviewed against the fixed narration. Approved-script dubbing still awaits the hosted fix. A separate silent source correctly returned `TRANSCRIPTION_EMPTY`. |
| Music and effects together | Passed: one call produced a video, music track, and effects track. All three URLs were readable; video contains H.264 and AAC and is 20 seconds long. |
| Free dubbing preview | Passed after deployment: explicit Spanish JSON-string language input started an eligible free preview. The result is a readable H.264/AAC video exactly 15 seconds long; returned metadata identifies the 22-second original, one language, and trimming. |
| Full video after preview | Language validation is fixed; the full-video/approved-script continuation remains untested. |
| Balance and trial lookup | Passed: actual decimal USD balance and per-service trial data returned through OAuth. |
| Credit-error guidance | Guide routes passed. Isolated authenticated MCP tests cover exhausted trials and insufficient balance with real billing/ledger code: no task, usage record, debit, or generation dispatch occurs. Production rejection and Codex's reply remain untested. |
| Continue after account update | Isolated authenticated MCP tests pass: a credit becomes visible on the same connection, reading balance does not retry, and one explicit resubmission creates one task and debit with the original arguments. No production funding change was performed; Codex's conversation behavior remains untested. |
| Usage examples | Bundled examples are present; selection and wording in a clean Codex session remain untested. |
| Generation status | Passed: existing successful and failed tasks retrieved; repeat lookup returned the same task and media URLs. A nonexistent task returned `Task not found`. |
| Multiple variants | Passed: one 10-second request with `variants_num=3` returned three distinct playable audio files. |
| Keep narration audible | Generation passed with `preserve_speech=true` and `ducking=true`: music, isolated vocals, ordinary mix, and ducked mix were returned. All four AAC files were readable; waveform comparison confirms source speech remains in both mixes. Listening quality and actual attenuation still need verification. |
| Timed sound effects | After deployment, the documented segments string is accepted and generation succeeds with a readable 22-second H.264/AAC video. Precise event timing and sound identity still need listening verification; successful transport and output duration do not prove those. |
| Instrument stems | Passed: all three variants returned drums, bass, vocals, and other tracks; all 12 stem URLs were readable. |

Media verification used ffprobe for actual file readability, codecs, and duration.
It does not establish subjective audio quality or speech intelligibility.

## Hosted blocker reproduced and resolved

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

PR #393 restores pre-parsed arrays to JSON strings before the argument model
validates them. It covers dubbing and the five exposed segment fields. Actual
FastMCP-dispatch regression tests reproduced 13 failures before the fix and
passed all 32 cases afterward. The latest broader MCP/segment/OAuth suite
passed 255 cases. After deployment, all six tools return their expected domain
validation errors for invalid arrays, rather than the old string/list error.
Valid Spanish dubbing and timed video-SFX inputs now create successful tasks.
Do not omit requested languages, which would select multiple defaults.

## OAuth test-client incident

The first temporary connection expired after waiting for authorization. On a
subsequent attempt, the callback completed but the Python client rejected the
token response because Clerk included `offline_access` in addition to `profile`.
The test client was restarted with both scopes explicitly requested, allowing
normal scope validation to remain enabled. Authenticated calls then succeeded.
Tokens are held only in the temporary client's memory.

Subsequent authenticated account calls succeeded while the browser still
displayed the consent page. Do not interpret that stale page alone as a failed
connection or click Allow repeatedly. This does not establish the cause of
every user's consent-page loading problem.

The plugin manifest remains `profile` only. The temporary Python client's
success alone did not establish Codex's authentication behavior. The separate
native Codex check below now covers initial sign-in and credential reuse, but
not token-expiry refresh or the complete installed-plugin conversation.

## Usage reconciliation

The initial run recorded three generation requests, including the no-speech
failure, and USD 0.0675 spending. The wallet decreased by that same amount.
The subsequent spoken-fixture subtitle and speech-preserving music runs used
one proofread trial and one video-to-music trial. The balance remained USD
4.0084. The post-deployment dubbing preview and timed-video-SFX runs each used
their remaining trial; both now report zero remaining and the balance is still
USD 4.0084. No account funding or automatic paid retry was performed.

## Spoken fixture and portal scan

The repository includes a synthetic English narration fixture in
`tests/fixtures/`, outside the distributable plugin. The 22-second video has a
19.055-second audio stream, including its trailing silence. Speech-preserving
audio outputs are approximately 19.1–19.2 seconds. The subtitle text matches
the fixed script; the Spanish translation preserves its meaning.

An aligned waveform comparison at 8 kHz found source-speech correlation of
0.9954 in isolated vocals, 0.8033 in the ordinary mix, and 0.9765 in the ducked
mix. This supports speech preservation; it is not a listening-quality score
or a measurement of the music attenuation envelope.

The earlier October 3 MCP deployment at `3b7a2c66` did not contain the fix.
The subsequent deployment at `946115c3` does, and both successful generation
retests above ran after the new container took over.

An energy-only check of the SFX output is inconclusive for event accuracy:
the 3–5 second interval has more energy than the requested 5–7 second rain
interval. This does not identify the sounds or establish the cause; do not
claim exact timing from this output without listening verification.

The current `sonilo-workflows-1.1.0.zip` was uploaded again. The portal changed
from Scanning to **Passed**. Navigation away from and back to Skills retained
the passed state. No review submission or publication was performed.

## Isolated credit recovery verification

Backend PR #393 includes two integration scenarios, for never-funded and
previously funded accounts. They drive the actual MCP ASGI transport and SDK,
OAuth verification with a locally signed test token, and real billing/ledger
services against an isolated in-memory database and Redis. Only media
generation dispatch and email notifications are stubbed. There is no change
to a production wallet or billing behavior.

Both zero-balance scenarios reject generation without creating a task, usage
record, or ledger debit. A local USD 1.2345 credit is visible on the same
authenticated connection. Reading that balance does not resume work. One
explicit resubmission using the original prompt/duration creates exactly one
task and one USD 0.1000 debit, leaving USD 1.1345. The combined OAuth integration
and JSON-dispatch suite passes all 45 cases. This verifies the backend contract,
not the plugin's natural-language reply, guide-link choice, or autonomous tool
selection; those still require the clean Codex test.

## Local installation and native Codex OAuth

The installed local marketplace still pointed at an older working directory
and reported version `0.3.0+codex.20260909195632`. Using the supported Codex CLI,
the Sonilo marketplace source was updated to the current release repository
and `sonilo@sonilo` was installed as **1.1.0**. All nine installed files match
the package source byte-for-byte. Codex's plugin reader reports it installed,
enabled, and containing the current `sonilo:sonilo-workflows` skill.

A separate Codex app-server diagnostic process used a process-only MCP entry
with the same production URL and configured `profile` scope. Codex itself
included `offline_access` in the authorization request. Its OAuth completion
notification returned `success: true`. After restarting the diagnostic
process, saved authentication still worked: `authStatus: oAuth`, no tool error,
and all 15 hosted tools, including `get_generation_task`, were returned.
The consent page remained visible even after successful authentication.

This test used Codex's own client rather than the Python SDK. It did not start
an agent turn or alter the plugin's scopes. It does not prove expired-token
refresh or the skill's behavior in a fresh conversation. The user's separate
`sonilo` stdio MCP entry is also still registered, so conversation tests must
verify they use the hosted tool inventory rather than its local Python tools.

Still needed: full-video and approved-script dubbing tests, the remaining
scenarios above, a clean v1.1.0 Codex conversation test, audio/timed-effect
listening verification, and current demo material.
