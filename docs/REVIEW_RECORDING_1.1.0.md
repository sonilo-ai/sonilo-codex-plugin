# v1.1.0 recording handoff

> Review outcome — October 21, 2026: OpenAI rejected v1.1.0 (email from openai-review to dev@sonilo.com; the portal shows only “Changes required”). Reasons given: the plugin “appears to enable or facilitate commerce for disallowed offerings (e.g., digital goods/services…)”, and the “plugin name or description did not meet our quality standards.” v1.0.0 stays published and publicly listed. No appeal was sent. The fix is tracked in `docs/REVISION_1.2.0_NOTES.md`. The status notes below are superseded.

> Submission update — October 5, 2026: user confirmed the six policy attestations at submission time. OpenAI Platform returned “Sonilo submitted for review”; the review version is read-only. v1.1.0 is awaiting a decision, not approved or published. This supersedes earlier pending-submission notes.

> Current status — October 5, 2026: submission preparation completed, with disclosed review risks. Final demo: https://cdn.sonilo.com/review/sonilo-v1.1.0-review-final-20261005.mp4 (217 seconds). It includes a newly submitted three-variant/stems music job, same-task retrieval, actual output audio, and an additional completed-task walkthrough. It is a ChatGPT web hosted-MCP recording, not a Codex skill recording or proof of every case on every client. The web run needed one follow-up to provide stem links, without regeneration. Reviewer balance after recording: USD 5.4491; dubbing trial remains exhausted. Portal reviewer notes were updated while retaining sign-in credentials and the pricing/billing-link disclosure. Legal attestations are unchecked; not submitted or published. Historical entries below are retained as dated evidence, not current blockers.


Record the actual installed plugin in Codex or the supported developer-mode
client. Show the prompt, actual tool invocation, returned result, and playback.
Do not present the listening page or a recreated transcript as a conversation
recording. Waiting periods may be edited out if the edit is labeled. Keep
passwords, OAuth codes, tokens, and unrelated account information off screen.

Use the synthetic 22-second spoken fixture:

https://raw.githubusercontent.com/sonilo-ai/sonilo-codex-plugin/e9fc90c4ce639fced00db16fca5e0530da2b0394/tests/fixtures/speech-demo.mp4

## Five positive cases

1. “What is my current cash balance, how many free text-to-music runs remain,
   and how much have I spent in the past 30 days?” Show separate current balance
   and historical usage; this does not generate media.
2. “Create three 10-second upbeat jazz music options for a product demo.
   Include separate drums and bass tracks for editing.” Show three distinct
   results and their actual stems; play one result.
3. “Create a cinematic 3-second whoosh sound effect.” Then separately request
   door closing at 2–3 seconds and rain at 5–7 seconds on the fixture, with no
   added effects elsewhere, and ask for a new video. Show actual outputs.
4. Ask for light cinematic music and subtle effects on the fixture, preserving
   speech and lowering music while people speak. Ask “Is that video ready?”
   while it is processing. Show reuse of the task ID and the final video.
5. Request Spanish subtitles first, inspect the returned Spanish SRT, then
   explicitly approve that file for Spanish dubbing of the same full source.
   Show the resulting full video and subtitles. In a separate conversation,
   request a free-only Spanish preview. The reviewer account has used this
   trial: the correct current response is no free preview, with no paid job.

The generation requests above may consume existing balance. Check actual
account data first. Record a real rejection honestly; do not automatically
retry, alter production funds, or reset trial counters to stage a result.

## Three negative cases

- “What kinds of music could work for a calm product demo?” Advice only.
- “Change the colors, typography, and transitions in my presentation video.”
  Explain the unsupported visual edits; do not generate unrelated audio.
- “Add music to https://127.0.0.1/private-video.mp4 and give me the finished
  video.” Reject the private URL without fetching it or calling Sonilo.

## Final handoff

Upload the genuine recording to a stable reviewer-accessible URL, replace the
draft's Demo Recording URL, and confirm it plays without extra access steps.
The existing recording is legacy evidence and must not be described as this
v1.1.0 walkthrough. Review the portal's legal/compliance attestations at the
time of submission. The help page's onward pricing/billing buttons are already
disclosed in reviewer notes; their acceptance is not established. Submission
and publication are separate actions, with publication requiring approval.
