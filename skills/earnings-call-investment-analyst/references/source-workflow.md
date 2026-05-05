# Original-Source Workflow

Use this reference when the task requires original filings, earnings releases, webcast replay assets, call audio, video, transcript evidence, or a reusable evidence pack.

## Source Ranking

Prefer sources in this order:

1. Company investor-relations page for the exact quarter.
2. SEC, exchange, or official filing archive.
3. Company-hosted earnings release, shareholder letter, deck, and supplemental financial tables.
4. Company-hosted webcast replay page, audio file, video file, subtitle file, or event JSON.
5. Official transcript if posted by the company.
6. Reputable third-party full transcript if no complete official transcript exists.
7. Third-party-hosted original call audio for targeted verification or fallback when no full transcript exists.
8. Financial media and analyst notes only as supporting context.

## Company-Original Source Rule

Use company-hosted original materials as the main evidence layer whenever possible. Do not let a third-party transcript or media summary replace the company earnings release, company investor presentation, company webcast replay, or official filing.

When company original sources are missing, label the gap explicitly:

- `company_original_status: found`
- `company_original_status: partial`
- `company_original_status: missing`
- `company_original_status: unavailable`

If a number differs across sources, trust the official company release or filing first, then explain the discrepancy.

## Evidence Folder Structure

For each earnings event, create one folder:

```text
artifacts/earnings/<ticker_or_company>/<fiscal_period>/
  source_inventory.json
  source_inventory.md
  webcast_assets.json
  evidence_pack.json
  evidence_pack.md
  raw/
    earnings_release.pdf
    investor_presentation.pdf
    10q_or_8k.html
    webcast_page.html
    replay_audio.mp3
    replay_video.mp4
    captions.vtt
  transcript/
    transcript_raw.txt
    transcript_timestamped.srt
    transcript_cn_notes.md
  analysis/
    earnings_review.md
```

Use stable filenames when possible. Keep the original URL and retrieval timestamp in JSON metadata.

## Agent-First Collection Policy

The collection workflow is agent-first, script-assisted. Start by using live web search, official IR pages, SEC/exchange pages, browser inspection, HTTP/page-source inspection, network requests, and direct downloads. Use scripts only when they save time, create a repeatable inventory, merge captions, transcribe audio, or package evidence.

Scripts are never a stopping condition. A script returning no assets, a 401/403, a JavaScript shell page, stale provider content, or a parser miss only means the agent must continue through another defensible route.

When scripts are used, record a compact script log:

| Field | Meaning |
|---|---|
| `script_used` | Script name and purpose |
| `script_result` | `found`, `partial`, `none`, `failed`, or `blocked` |
| `script_limitation` | Missing input support, 401/403, JS-only page, no recording, stale provider, parser miss, or other limitation |
| `manual_fallback_path` | The web/browser/HTTP/network/direct-download route used after the script |
| `final_source_type` | Source type used for final work, such as `company_original`, `regulatory_filing`, `official_event_platform`, `third_party_transcript`, or `original_call_audio` |

## Collection Heuristics

Use the route that best fits the live source problem. Do not execute these as a required sequence.

- Start from likely authoritative material: company IR, exchange/SEC filings, official event pages, earnings releases, presentations, and supplemental tables.
- Look for complete call content through whichever route is most efficient: official transcript, replay, audio/video file, captions, event-platform payloads, browser/network inspection, search results, direct HTTP, page source, or reputable third-party transcript/audio.
- Treat provider names such as StockAnalysis, Quartr, Motley Fool, Seeking Alpha, Benzinga, Alpha Spread, and EarningsCall.biz as search seeds and examples, not a mandatory provider checklist.
- Optionally run `scripts/source_discovery.py` to create a repeatable official-source inventory. If automation input has exact report date, call date, call URL, or fiscal period that the script does not accept, preserve those fields manually in notes or the evidence pack.
- Optionally run `scripts/webcast_asset_fetcher.py` on an official webcast or replay page as a first-pass asset probe. If it returns only adapter JSON, static scripts, 401/403, JavaScript shells, or no recording/transcript, record that limitation only if useful and continue through another route.
- If the webcast exposes an HLS caption playlist, optionally run `scripts/caption_playlist_fetcher.py --playlist-url <subtitles.m3u8>` and treat the output as official event-platform captions, not as a substitute for audio-first transcription. Check the manifest's `playlist_complete`; when it is false, the playlist may be only a sliding live/DVR window.
- If a reputable third-party full transcript and original call audio are both available, use the full transcript as the primary working source. Use the audio for targeted verification of decision-useful wording, disputed passages, and transcript quality issues. Do not run full-audio ASR by default.
- If no reputable full transcript is available, the user explicitly asks for audio-first analysis, or spot checks reveal material transcript-quality problems, run `scripts/audio_transcriber.py --check-deps`, then transcribe the replay audio or video. Prefer the project ASR venv with `--provider faster-whisper --device auto --compute-type auto`; use `ffmpeg` for audio extraction when available, or `--no-ffmpeg` only when PyAV can read the source media directly. Use Whisper CLI or OpenAI only as fallback providers.
- Use `scripts/earnings_pack_builder.py` only when enough structured source, transcript, actuals, guidance, or consensus inputs exist. If evidence was collected manually, create the same source notes manually instead of forcing the pack builder.
- Analyze the evidence with the main skill workflow in `SKILL.md`.

## Fallback Source Notes

When official call material is incomplete, record the fallback routes that materially affected confidence or source selection. Keep this compact; do not fill rows for providers that were not useful or were not checked.

| Route or Provider | Status | URL | Source Type | Complete? | Access/Failure Note | Used? |
|---|---|---|---|---|---|---|
| Example provider or route | `found/stale/missing/blocked/partial` |  | `third_party_transcript` / `original_call_audio` / `media_or_analyst` | `yes/no/partial/unknown` |  | `yes/no` |

Use `blocked` for 401/403, login wall, bot wall, or scripts that cannot fetch the page. Use `stale` when the provider has older quarters but not the target call.

## Provisional Output Gate

If official transcript, official replay, official audio/video, and official complete captions are missing, but a reliable third-party transcript or third-party-hosted original audio is available:

- Set `provisional: true`.
- State `fallback_completed: true` only when the agent has either obtained complete reliable call content or made a reasonable source-specific search and clearly documented remaining gaps.
- List `missing_materials`.
- Include `recheck_after` with a concrete date/time for the official IR/event-platform replay/transcript.
- Keep financial actuals sourced to official release/filings even when call commentary uses a third-party transcript.

## Evidence Hygiene

- Keep official filings separate from media commentary.
- Preserve raw source links; do not only keep summaries.
- Do not treat page captions as authoritative when the user asks for audio-based transcription.
- Do not treat an incomplete HLS caption playlist as the full call transcript.
- Do not perform full audio transcription when a reputable full transcript is already available unless the user asks for it or transcript quality is materially suspect.
- If the only complete audio is hosted by a transcript/audio aggregator rather than the company or event platform, label the content as original call audio and the hosting path as third-party hosted. Cross-check material claims against official sources.
- If captions and audio transcription disagree on a decision-useful phrase, flag it and prefer the audio-derived transcript after checking the timestamp.
- Label uncertain transcript segments.
- Do not infer customer identity, end-market destination, or regulatory approval from vague management wording.
- For export-control-sensitive companies, separate shipment origin, shipment destination, end customer, and end user.

## Minimum Evidence Pack

For a serious post-earnings review, try to collect:

- Earnings release.
- Actual reported financial table.
- Prior-quarter guidance.
- Consensus estimates.
- Current guidance.
- Call transcript or audio replay.
- Stock price reaction.
- Management Q&A comments on the top thesis variables.

If any item is missing, state the gap in the final analysis.
