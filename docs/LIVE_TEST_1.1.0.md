# v1.1.0 verification — October 2–3, 2026 (Pacific)

**Release status: hosted fixes, media verification, desktop connection, and refusal checks passed. Updated recording and review submission remain.**

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
| Subtitle review before dubbing | Subtitle generation passed on the synthetic spoken fixture: six English cues and their Spanish translations were returned, downloaded, and reviewed against the fixed narration. After PR #398, the same approved Spanish SRT passes preflight and produces a readable full 22-second video and aligned SRT; all six cues retain the approved text. A separate silent source correctly returned `TRANSCRIPTION_EMPTY`. |
| Music and effects together | Passed: one call produced a video, music track, and effects track. All three URLs were readable; video contains H.264 and AAC and is 20 seconds long. |
| Free dubbing preview | Passed after deployment: explicit Spanish JSON-string language input started an eligible free preview. The result is a readable H.264/AAC video exactly 15 seconds long; returned metadata identifies the 22-second original, one language, and trimming. |
| Full video after preview | Passed after PR #398: the 15-second preview was followed by a request using the original 22-second video and approved Spanish subtitles. Both delivered video and audio are 22 seconds; no preview metadata appears in the full result. |
| Balance and trial lookup | Passed: actual decimal USD balance and per-service trial data returned through OAuth. |
| Credit-error guidance | Guide routes passed. Isolated authenticated MCP tests cover exhausted trials and insufficient balance with real billing/ledger code: no task, usage record, debit, or generation dispatch occurs. Production rejection and Codex's reply remain untested. |
| Continue after account update | Isolated authenticated MCP tests pass: a credit becomes visible on the same connection, reading balance does not retry, and one explicit resubmission creates one task and debit with the original arguments. No production funding change was performed; Codex's conversation behavior remains untested. |
| Usage examples | Bundled examples are present; selection and wording in a clean Codex session remain untested. |
| Generation status | Passed: existing successful and failed tasks retrieved; repeat lookup returned the same task and media URLs. A nonexistent task returned `Task not found`. |
| Multiple variants | Passed: one 10-second request with `variants_num=3` returned three distinct playable audio files. |
| Keep narration audible | Generation passed with `preserve_speech=true` and `ducking=true`: music, isolated vocals, ordinary mix, and ducked mix were returned. All four AAC files were readable; waveform comparison confirms source speech remains in both mixes. Windowed mixture analysis measures about 10.5 dB lower music during speech than the ordinary mix, with recovery in pauses. The user subsequently listened to the review page and reported no issues. |
| Timed sound effects | After deployment, the documented segments string is accepted and generation succeeds with a readable 22-second H.264/AAC video. The user subsequently listened to the review page (including the requested door/rain intervals) and reported no issues. This is human acceptance of the sample, not a guarantee of model accuracy on all inputs. |
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

## Approved-subtitle preflight configuration blocker resolved

The full-video continuation used the original 22-second fixture and the
reviewed Spanish SRT returned by proofread. It failed before task creation
with `Subtitle validation is temporarily unavailable, please retry`.
Production logs identify an empty Bearer header in the preflight client;
MCP ECS revision 95 lacks `DUBBING_API_AUTH_KEY`. Public API and worker task
definitions already inject this existing secret. Ordinary preview generation
succeeds because its work runs in the configured worker, whereas supplied
subtitles must be checked in the MCP request handler before billing.

The failed call left the balance unchanged at USD 4.0084 and created no
returned generation task. Do not retry blindly or discard approved subtitles.
[PR #398](https://github.com/sonilo-ai/sonilo-api-dashboard/pull/398) adds
the existing secret reference to MCP and a regression
check covering both public and MCP preflight surfaces; the new check fails
against the old configuration and passes with the mapping. Its complete CI
passed 3,130 tests (19 skipped), and it merged as `e3f08de0`.
[Deployment run 37152729311](https://github.com/sonilo-ai/sonilo-api-dashboard/actions/runs/37152729311)
succeeded. ECS revision 96 reached COMPLETED with one running task and no
pending tasks; its image matches the merge commit and its secret mapping is
present. The same approved Spanish SRT now passes preflight (six cues, no
issues) and completes a full-video task. ffprobe confirms 22-second H.264
video and 22-second AAC audio. All six aligned SRT cues preserve the approved
text exactly. Subtitle export succeeded with one informational
`zero_duration_characters` notice for one character in cue 1; every exported
cue has a positive duration. This does not establish subjective voice quality.

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
USD 4.0084. The failed preflight also left that balance unchanged. After
deploying the credential fix, one explicit full-video retest charged USD
1.2797, leaving USD 2.7287. Usage reports eight requests and USD 1.3472 total
spending, matching the original balance minus current balance. No production
account funding was changed or ambiguous request blindly resubmitted.

## Spoken fixture and portal scan

The repository includes a synthetic English narration fixture in
`tests/fixtures/`, outside the distributable plugin. The 22-second video has a
19.055-second audio stream, including its trailing silence. Speech-preserving
audio outputs are approximately 19.1–19.2 seconds. The subtitle text matches
the fixed script; the Spanish translation preserves its meaning.

An aligned waveform comparison at 8 kHz found source-speech correlation of
0.9954 in isolated vocals, 0.8033 in the ordinary mix, and 0.9765 in the ducked
mix. This supports speech preservation; it is not a listening-quality score.

A subsequent mixture analysis aligned the separately returned vocal and music
tracks to each mix at 8 kHz, then fitted their gains in 250 ms windows. Median
relative fit residuals were 1.41% (ordinary mix) and 1.61% (ducked mix). After
excluding weak music and high residuals, 62 speech windows and 11 quiet windows
remained in each mix. Median music gain during speech was 0.4232 in the
ordinary mix and 0.1270 in the ducked mix: about 10.5 dB attenuation. The ducked
music gain increased to a 0.1772 median in quiet windows and rose across the
final quiet tail from 0.1772 to 0.2876. This establishes attenuation and recovery
for this output, not subjective intelligibility or a guarantee for every input.

A local listening page at `http://127.0.0.1:8123/` compares the actual ordinary
and ducked mixes, timed SFX, 15-second preview, and 22-second full dub. All five
browser players loaded without media errors; the SFX jump control seeks to
5 seconds without autoplay. Files and signed media links remain outside Git.
On October 3, the user reported that the listening page sounded correct with no issues, resolving the subjective acceptance check. This page is a
result comparison, not a substitute for a fresh Codex conversation demo.

The earlier October 3 MCP deployment at `3b7a2c66` did not contain the fix.
The subsequent deployment at `946115c3` does, and both successful generation
retests above ran after the new container took over.

An energy-only check of the SFX output is inconclusive for event accuracy:
the 3–5 second interval has more energy than the requested 5–7 second rain
interval. This does not identify the sounds or establish the cause; do not
claim exact timing from the energy check alone. The user subsequently listened
to the review page and accepted the sample.

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

Still needed: fresh conversation verification and current demo material. On
October 3 the user authorized a temporary Codex test task and accepted the
listening page. The task was created for account lookup, existing full-dub
retrieval, and usage examples, without generation or account changes. Its
first run did not pass: the installed 1.1.0 skill was selected, but only the
legacy local `mcp__sonilo__get_account_services` was available and it returned
`Invalid SONILO_API_KEY`. Hosted `get_generation_task` was absent. No generation
or account mutation occurred. Native default-config diagnostics likewise find
the installed plugin's declared `sonilo` MCP server, but runtime inventory shows
the legacy stdio server only. Disabling that legacy server in a temporary
process yields no hosted Sonilo tools; the user's actual settings are unchanged.
This first failure was not a successful installed-plugin test and did not
establish a hosted-backend regression. See the follow-up below.

## Public sample-link cleanup

The live 1.0.0 directory page includes an internal review-source URL in its
third starter prompt. This is distinct from the review recording field. The
1.1.0 portal draft and manifest omit that fixed URL; the remaining prompts now
use ordinary wording rather than asking users to understand public-HTTPS
terminology before they start. Media URL validation remains in the skill.
The live page will retain its current prompt until an approved update is
published. Do not delete the old sample while published prompts or review
cases still reference it. A future one-click sample should be an intentionally
public, rights-cleared asset on a stable examples URL, not a temporary reviewer
fixture.


## Hosted/local MCP name collision repair (October 3)

A controlled package-only change from the MCP key `sonilo` to `sonilo_platform`
resolves the connection collision in a fresh Codex app-server process, without
changing the user's global stdio configuration or injecting a replacement MCP
entry. Before the rename, the runtime exposed only the legacy local schemas.
After reinstalling the renamed plugin, it identifies the production HTTPS
origin and requests OAuth. Native OAuth completed successfully with the same
account and scopes; inventory then reports `authStatus: oAuth`, no tool error,
and all 15 hosted tools, including `get_generation_task`.

The skill dependency and reconnect instructions now use `sonilo_platform`.
Workflow guidance explicitly prevents falling back to the legacy local server.
The release checker enforces the distinct server key and matching dependency.
All nine installed files match the current package source. Both ZIPs were
rebuilt, and the revised Skill ZIP was uploaded to the existing 1.1.0 draft.

The running desktop app still exposes only legacy tools in both the existing
and a newly created temporary test chat. Those chats correctly stop without
calling the old server; they do not establish successful balance/task reads.
A separate CLI attempt to resume the existing chat was rejected because the
desktop app owns its active writer; no writer lock was removed. Do not count
successful standalone discovery as proof that the desktop cache has refreshed.


A fresh ephemeral Codex CLI conversation using the normal installed plugin
(no MCP config override, no direct SDK/HTTP fallback) passed both reads:
`mcp__sonilo_platform__get_account_services` returned cash balance `2.7287`
USD and the actual exhausted music/dubbing trial counts;
`mcp__sonilo_platform__get_generation_task` retrieved the existing successful
Spanish full dub with video and SRT. Both tool calls completed once, with no
new generation or charge. This verifies the installed plugin in a restarted
Codex runtime; the desktop process still requires a reload/restart and retest.
Local release validation and `git diff --check` pass. After the new upload
completed, reloading the portal and returning to Skills showed **Passed** for
the revised ZIP. This verifies its scanner result, not plugin review approval.


## October 4 desktop acceptance and submission preparation

The desktop conversation now exposes `sonilo_platform` alongside the legacy
local server. Direct hosted `get_account_services` and `get_generation_task`
calls succeed. Account data initially reported USD 2.7287; the existing full
Spanish dub returned succeeded, video, and SRT. This resolves the desktop
connection blocker above; no legacy tool was used.

The temporary desktop acceptance chat passed six scenarios: account lookup,
existing-task continuation, an explanation-only preview/full-version question,
rejection of loopback and local-file media inputs, capability advice without
generation, and a nonexistent task returning `Task not found` without retry.
The three exact portal negative prompts were also checked independently:
creative music advice, unsupported visual editing, and HTTPS loopback media.
All three caused zero Sonilo calls. A separate `get_usage(days=30)` call passed
and was correctly distinguished from cash balance.

Portal test cases now use the immutable 22-second synthetic spoken fixture
instead of the old temporary reviewer-source URL. The music case requests
10-second variants, matching the successful generation; timed effects include
the final 7–22 second quiet interval. Reviewer notes disclose the guide's
View pricing / View billing buttons and explicitly state that the replacement
walkthrough is still pending. The used dubbing trial is disclosed: a free-only
request must stop rather than silently become a paid job.

The native computer-use tool rejected Terminal access, so an actual CLI screen
recording could not be captured with that tool. No output montage, rendered
transcript, or results page was substituted for a real plugin recording.
The previous recording URL remains in the draft and is marked as incomplete
coverage in the reviewer notes. The final page requires explicit acceptance
of OpenAI terms plus compliance, rights, and age-suitability attestations;
these remain unchecked. No submission or publication has occurred.


Two additional production generations on October 4 completed successfully
through the installed hosted tools: a 3-second cinematic text sound effect,
and the 22-second spoken fixture with combined music/effects,
`preserve_speech=true`, and `ducking=true`. The latter returned a new video,
music, effects, and processed-music tracks. The balance changed from USD
2.7287 to USD 2.4065 (USD 0.3222 for these tests). Earlier user listening
acceptance applies to the previous samples, not these new outputs.
The recording handoff is in [REVIEW_RECORDING_1.1.0.md](REVIEW_RECORDING_1.1.0.md).
