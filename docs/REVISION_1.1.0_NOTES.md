# Revision 1.1.0 draft notes

> October 3 live-test update: **not release-ready**. Backend PRs #393 and #398
> are merged and deployed; the latest full CI passed 3,130 tests (19 skipped).
> Live dubbing preview, full approved-script continuation, and timed-SFX
> generation succeed, and the user accepted the listening page. Clean Codex
> conversation checks and a current recording remain. The latest connection
> routing revision passed its new Skill scan. Music variants, stems, combined output, subtitle generation,
> speech-preserving output retrieval, balance, and task retrieval passed the
> checks described in [the live verification report](LIVE_TEST_1.1.0.md).
> Earlier preparation notes below do not supersede these findings.


## Release notes

Update the bundled Sonilo workflow skill and directory description to cover subtitle review before dubbing, eligible single-language dubbing previews, user-requested full-video continuation, combined music and sound effects, music variants and stems, timed effects, speech preservation, and task retrieval after interruptions.

Account status now reports the authenticated account's current USD cash balance and service-specific free-trial allowance. Historical spending is kept separate from balance. Missing balance data is reported as unavailable, and a balance snapshot is not treated as a guarantee that a generation can run.

Credit errors do not trigger automatic resubmission. The skill does not direct users to pricing, checkout, subscriptions, or credit recharge, and suppresses purchase instructions returned by tools. Confirmed credit rejections now include the published Balance and free trials guide in the conversation language. Ten language routes are configured, with English as fallback. The guide retains public navigation and View pricing / View billing buttons; their acceptance in this flow is not yet confirmed by OpenAI review.

The MCP endpoint remains https://api.sonilo.com/mcp with OAuth scope profile. The account-balance backend update has been deployed. This revision updates the plugin instructions and metadata; it adds no local executable or additional OAuth scope.

## Validation recorded for this package

- Plugin manifest and bundled skill validators passed.
- Local release checks and production HTTP/OAuth-discovery checks passed.
- The ZIP contents match the plugin source.
- Hosted MCP account serialization, precision, account isolation, and refresh behavior were covered in backend PR #384; its merged CI passed and deployment completed.
- No paid media-generation run or new demonstration recording was performed for this revision during preparation. Existing review assets must not be represented as recordings of the new features.

## Previously saved portal draft (before the October 2 guide update)

https://platform.openai.com/plugins/edit/asdk_app_6a56e50ff2788191a96c7c8cd84bb6c2/asdk_app_v_6ab83efe20c881919ee5a4ba03af2966

Saved version 1.1.0, subtitle and description, three prompts, nine existing translations, five positive and three negative test cases, refreshed MCP annotations (15 tools / 45 justifications), and release notes. The dedicated reviewer password sign-in path was verified; its instructions now explain the optional “Use another method” step. No reviewer credentials are copied into this repository.

Uploaded `dist/sonilo-workflows-1.1.0.zip` to the Skills section. The platform scanner returned “Error” with “An error occurred while scanning. Rescan to try again.” Rescanning and reuploading did not resolve it. This is a scanner error, not a stated policy rejection; no more specific reason was shown.

The draft is saved but not ready to submit: the Skill scan must succeed, the new media cases need an actual end-to-end run, and the inherited demo recording has not been updated for the new features. Compliance attestations are unchecked. No review submission or publication was performed.

## October 2 package update

The local source and both rebuilt ZIPs now include the deployed multilingual
balance guide and updated examples. All 10 public guide routes returned HTTP
200 with the correct canonical URLs. Local release checks and skill validation
passed, and each ZIP entry was compared byte-for-byte with its source. The
previously saved portal draft and upload described above predate this change;
they must not be treated as the updated package or a successful scan.

## October 2 subsequent verification

The current Skill ZIP was reuploaded and the portal scanner returned **Passed**.
That state persisted when leaving and reopening Skills. This resolves the
earlier scan error only; compliance attestations remain unchecked and no review
submission or publication has occurred. The existing recording still needs to
be replaced by a demonstration of the updated workflows. See the live report
for current production results and remaining release gates.
