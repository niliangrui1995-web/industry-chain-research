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

## Collection Sequence

1. Run `scripts/source_discovery.py` with ticker, company name, quarter, and fiscal year.
2. Open the resulting `source_inventory.md` and decide which official URLs matter.
3. Run `scripts/webcast_asset_fetcher.py` on the official webcast or replay page.
4. If the webcast exposes an HLS caption playlist, run `scripts/caption_playlist_fetcher.py --playlist-url <subtitles.m3u8>` and treat the output as official event-platform captions, not as a substitute for audio-first transcription. Check the manifest's `playlist_complete`; when it is false, the playlist may be only a sliding live/DVR window.
5. If the official page does not expose a complete transcript, audio replay, or video replay, inspect fallback transcript/audio paths before giving up. Use StockAnalysis and Quartr first, then Motley Fool, Seeking Alpha, Benzinga, Alpha Spread, and EarningsCall.biz. Run `scripts/webcast_asset_fetcher.py` on the chosen fallback page and label complete recordings as original call audio with third-party hosting.
6. If a reputable third-party full transcript and original call audio are both available, use the full transcript as the primary working source. Use the audio for targeted verification of decision-useful wording, disputed passages, and transcript quality issues. Do not run full-audio ASR by default.
7. If no reputable full transcript is available, the user explicitly asks for audio-first analysis, or spot checks reveal material transcript-quality problems, run `scripts/audio_transcriber.py --check-deps`, then transcribe the replay audio or video. Prefer the project ASR venv with `--provider faster-whisper --device auto --compute-type auto`; use `ffmpeg` for audio extraction when available, or `--no-ffmpeg` only when PyAV can read the source media directly. Use Whisper CLI or OpenAI only as fallback providers.
8. Run `scripts/earnings_pack_builder.py` to create `evidence_pack.json` and `evidence_pack.md`.
9. Analyze the evidence with the main skill workflow in `SKILL.md`.

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
