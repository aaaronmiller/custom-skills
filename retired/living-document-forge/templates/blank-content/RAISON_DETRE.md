# RAISON D'ETRE: This Living Document

This is a living document: a browser-native, addressable review surface for asynchronous human-agent collaboration.

It exists because chat is the wrong protocol for sustained review. Agents can generate thousands of words in seconds; humans read, compare, annotate, and decide at human speed. In chat, the human races the next reply, loses scroll position, cannot attach durable comments to precise claims, cannot bind media to propositions, and cannot inspect long-running agent work as structured history.

This document is different. It is spatial, persistent, asynchronous, multimedia, and organized around stable sections, proposals, annotations, changelogs, and immutable worklogs.

Core contract:

- stable section IDs make every claim addressable;
- annotations attach review state to exact targets;
- proposals are approved, rejected, or deferred individually;
- worklogs append what agents changed, validated, skipped, and recommend next;
- changelogs summarize meaningful releases separately from granular history;
- local drafts stay visibly local until exported or applied;
- agent handoffs use structured change-request JSON;
- the browser is the primary review surface, while the terminal is for validation and packaging.

This document is a sibling to an LLM wiki, not a replacement for one. Wikis optimize settled knowledge for retrieval. Living documents optimize unsettled work for refinement, review, and decision history. Wikis may link here for active debates; this document may link back to wiki pages for settled definitions.

The canonical working form is a folder, optionally named with a `.livingdoc` suffix. Archives are for distribution, not daily use.

## Version contract

The document declares its format and skill compatibility in `public/content/index.json`. An agent must check that block before making changes. If migration is required, it should follow the migration guide, update metadata narrowly, and append a worklog. Pure migrations must not rewrite content, proposals, annotations, or history.

Raison d'etre means reason for being. This file is the first thing a human or agent should read before operating on the document.
