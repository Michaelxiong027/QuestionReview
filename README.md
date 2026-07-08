# QuestionReview

QuestionReview is a local workflow for reviewing English homework or exam questions from an education platform. It downloads page screenshots, answer screenshots, and platform API payloads from the URLs in `questions.xlsx`; Codex then performs a visual review, writes the review results back to Excel, and can submit confirmed platform-answer corrections back to the platform.

The review decision must be based on visual evidence and platform payloads, not OCR output. Some script names still contain `ocr` for historical reasons, but OCR is not the final source of truth.

## Repository Contents

- `questions.xlsx`: Local task workbook. It is intentionally ignored by Git because it contains task data.
- `authorization.txt`: Local platform API authorization token. It is ignored by Git.
- `task_runner_question_ocr_multithread.py`: Reads the workbook, calls the platform API, downloads full-page screenshots, answer screenshots, and platform JSON payloads.
- `qr_audio_extractor.py`: Attempts to decode listening-question QR codes and extract audio when available.
- `build_initial_review_results.py`: Builds a conservative initial `_codex_review/results.json` from a downloaded run.
- `make_review_contact_sheets.py`: Generates contact sheets that combine the source page and answer screenshots for easier visual review.
- `codex_visual_review_writer.py`: Writes `_codex_review/results.json` back into `questions.xlsx`.
- `platform_answer_modifier.py`: Submits confirmed answer corrections back to the platform.
- `codex_review_finalize.py`: Convenience script that can submit platform modifications and write Excel results in one step.
- `cloud_link_uploader.py` and `upload_to_cloud_link.bat`: Optional Baidu cloud upload helpers.
- `config.cloud.example.json`: Example cloud upload configuration.

## Ignored Local Data

The repository intentionally excludes local task data, secrets, generated screenshots, review outputs, virtual environments, and bundled binary tools. Important ignored paths include:

- `.venv/`
- `authorization.txt`
- `baidu_cookie.txt`
- `config.cloud.json`
- `questions.xlsx`
- `screenshots/`
- `_codex_review/`
- `_codex_review_archive_*/`
- `.agents/`, `.codex/`, `.codexbridge/`
- `tools/`

## Setup

Create or reuse the local virtual environment, then install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-qr.txt
```

Place the current task files in the project root:

```text
questions.xlsx
authorization.txt
```

Both files must exist and must not be empty before running the downloader.

## Full Workflow

### 1. Download Platform Materials

```powershell
.\.venv\Scripts\python.exe .\task_runner_question_ocr_multithread.py --excel .\questions.xlsx --workers 4
```

After the command finishes, verify that:

- `screenshots/<run_id>/manifest.json` exists.
- The downloaded count matches the number of URL rows in the workbook.
- There are no failed downloads. If any downloads fail, fix the download issue and rerun before reviewing.

Each downloaded page directory contains materials such as:

- `source_page.jpg`: Full original page screenshot.
- `answer/*.png`: Platform-answer screenshots. The highlighted area is the current platform answer.
- `platform_response.json`: Original platform API payload.
- Manifest entries containing `row`, `position`, `page_id`, `book_id`, `questions`, `platform_answers`, and screenshot paths.

### 2. Handle Listening Questions

When a question appears to be a listening question, first try to extract the audio:

```powershell
.\.venv\Scripts\python.exe .\qr_audio_extractor.py
```

Review listening questions using the question page, answer screenshots, platform payload, independent answer images, QR-code result, and extracted audio when available.

Do not guess listening answers from the static page alone. If the QR code, audio, and independent answer image cannot provide enough information, mark the item as needing manual confirmation.

### 3. Build or Update Review Results

A conservative initial results file can be generated with:

```powershell
.\.venv\Scripts\python.exe .\build_initial_review_results.py --run-dir .\screenshots\<run_id> --output .\_codex_review\results.json
```

Codex then performs the visual review and updates `_codex_review/results.json`.

Every URL row must receive a final status in the same review pass. Do not leave rows in a pending visual-review state when delivering final results.

Visual review is a default required step for every task run. After any URL input workbook is processed, the completed review results must be written back to `questions.xlsx` unless the project owner explicitly requests a different final workbook.

### 4. Optional Contact Sheets

To make review easier, generate contact sheets:

```powershell
.\.venv\Scripts\python.exe .\make_review_contact_sheets.py --run-dir .\screenshots\<run_id> --limit 10
```

For specific manifest positions:

```powershell
.\.venv\Scripts\python.exe .\make_review_contact_sheets.py --run-dir .\screenshots\<run_id> --positions 1 2 3
```

## Review Rules

Use Codex visual review as the final judgment. Do not use OCR output as the final source of truth.

Platform answers come from:

- `manifest.json` under `questions[].platform_answers`
- the corresponding `answer/*.png` screenshots
- `platform_response.json`, especially the real `labelContainer.sequence`

Important rules:

- Use `platform_answers`; do not assume an `answers` field exists.
- For first-letter completion questions, the platform may only store the missing part. Do not mark it wrong just because the full word is not stored.
- If a circled-answer or image-matching question visually matches the prompt, mark it as correct.
- If the source text is missing, the page is incomplete, or there is no unique correct answer, do not invent an answer. Mark it as needing manual confirmation.
- For non-listening placeholder answers such as omitted or ellipsis answers, first try to determine the real answer visually. If a unique answer can be confirmed, submit a correction. If the answer is open-ended or cannot be uniquely determined, mark it as needing manual confirmation.
- For listening questions, attempt QR/audio/independent-answer-image review first. If those sources do not provide enough evidence, mark it as a listening item that cannot be identified.

## `results.json` Format

Use row numbers as top-level keys. The writer currently reads `correct_answers`, not `correct_answer`.

### Correct Row

```json
{
  "status": "All correct",
  "correct_answers": "",
  "analysis": "Codex visual review found the page and platform answers consistent; no platform correction needed.",
  "answer_updates": [],
  "error_images": []
}
```

### Confirmed Platform Answer Error

```json
{
  "status": "Incorrect, corrected",
  "correct_answers": "Question 1: B",
  "analysis": "Explain why the platform answer is wrong and why the new answer is correct.",
  "answer_updates": [
    {
      "sequence": "real platform sequence from platform_response.json",
      "answer_index": 1,
      "old_answer": "current wrong platform answer",
      "new_answer": "correct answer",
      "new_answer_rich_text": "<p>correct answer</p>"
    }
  ],
  "error_images": [
    "path to one answer/*.png screenshot showing the original wrong platform answer"
  ]
}
```

Requirements for corrected rows:

- Keep exactly one error screenshot for each corrected row.
- `error_images` must point to an `answer/*.png` screenshot from the corresponding URL.
- `sequence` must be the real `labelContainer.sequence` from `platform_response.json`.
- A sanitized screenshot filename such as `44_20` must not be used as a replacement for the real platform sequence `44: 20`.
- For multiple-choice questions, submit the option letter.
- For fill-in, translation, and sentence-ordering questions, submit the answer text.
- For grouped matching questions, submit answers in question order when that is the platform format.

### Needs Manual Confirmation

```json
{
  "status": "Needs manual confirmation",
  "correct_answers": "",
  "analysis": "Explain why the answer cannot be uniquely confirmed.",
  "answer_updates": [],
  "error_images": []
}
```

### Listening Content Not Identifiable

```json
{
  "status": "Listening content not identifiable",
  "correct_answers": "",
  "analysis": "QR code/audio/independent answer image was checked, but the listening content could not be obtained or confirmed.",
  "answer_updates": [],
  "error_images": []
}
```

## Write Results Back to Excel

```powershell
.\.venv\Scripts\python.exe .\codex_visual_review_writer.py --excel .\questions.xlsx --results .\_codex_review\results.json
```

Verify that:

- Status, correct answers, analysis, and error screenshots are written into the workbook.
- Every corrected row has exactly one platform-answer screenshot.
- No rows remain pending.

## Submit Platform Corrections

Always run a dry run first:

```powershell
.\.venv\Scripts\python.exe .\platform_answer_modifier.py --results .\_codex_review\results.json --run-dir .\screenshots\<run_id> --dry-run
```

The dry run must report `failed = 0`.

Once the dry run passes, submitting corrections through `platform_answer_modifier.py`
is considered pre-authorized by the project owner for this workflow. Do not ask for
additional confirmation before calling the platform modification API, unless the
requested action is outside the reviewed `answer_updates` workflow or the dry run
reports any failure.

Then submit for real:

```powershell
.\.venv\Scripts\python.exe .\platform_answer_modifier.py --results .\_codex_review\results.json --run-dir .\screenshots\<run_id>
```

If non-ASCII answers must be submitted, use the current `platform_answer_modifier.py` logic. It serializes JSON with `ensure_ascii=False`, sends UTF-8 bytes, and includes `charset=utf-8` in `Content-Type`.

After submission, inspect `_codex_review/platform_modifications.json`. All rows with `answer_updates` must be `success` or a confirmed safe `skipped`. There must be no `failed` rows.

To force resubmission for a row that was already marked successful:

```powershell
.\.venv\Scripts\python.exe .\platform_answer_modifier.py --results .\_codex_review\results.json --run-dir .\screenshots\<run_id> --force-row ROW_NUMBER
```

## Final Validation

A completed run should satisfy:

- The number of records in `_codex_review/results.json` equals the number of URL rows in the workbook.
- Pending visual-review count is `0`.
- `questions.xlsx` has been written back.
- Every corrected row has exactly one original platform-answer screenshot.
- `_codex_review/platform_modifications.json` has no `failed` entries.

## Optional Cloud Upload

The Baidu cloud upload helpers are optional and are not required for the main review workflow. Use them only when result files must be uploaded and shared.
