# Privacy Policy

Last updated: 2026-11-04

JTBD Base is a Claude Code plugin made of skills, agents, reference files and a local Python script. It has no server, no account, no telemetry and no analytics. The author receives no data from people who use it.

## What the plugin reads

- Files you place in the `inbox/` folder of your project: interview transcripts, research notes, survey exports, support tickets. These can contain personal data such as names, email addresses or company names.
- Your knowledge base: Markdown files in your project folder (local backend) or the Notion pages and databases you set up (Notion backend).
- `jtbd.config.yaml`, which holds your backend choice, project names and Notion IDs.

Claude reads these files during your Claude Code session, under the terms that apply to your use of Claude.

## What the plugin stores, and where

- **Local backend:** entries are written as Markdown files in your project folder, on your machine.
- **Notion backend:** entries are written to your own Notion workspace through the Notion connector you installed and authorized. Notion's own privacy policy applies to that data.
- Generated deliverables (interview guides, screeners, briefs) are written to `outputs/` in your project folder.

By default, only short anonymized quotes go into the base, with participant codes (P01, P02) instead of names, and no email addresses or company names. The plugin keeps names only if you explicitly ask it to. The lint and the auditor agent flag quotes that look like they contain personal data. Raw transcripts are never uploaded by the plugin: they stay in `inbox/`.

## What the plugin sends elsewhere

Nothing, apart from the Notion backend described above, which you choose and authorize yourself. The plugin declares no connector and calls no other external service.

## Retention and deletion

The plugin retains nothing on its own. Your data lives in your project folder or your Notion workspace, and you can edit or delete it at any time. The plugin itself never deletes entries: it marks them Deprecated.

## Children

The plugin is a professional research tool and is not intended for people under 18.

## Contact

Questions or concerns: open an issue at https://github.com/yulldesign/jtbd-base/issues.
