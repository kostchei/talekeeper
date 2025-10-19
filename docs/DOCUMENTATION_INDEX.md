# TaleKeeper Documentation Index

Last Updated: 2025-10-19

## Main Implementation Guide

**[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - THE definitive guide to understanding the current TaleKeeper codebase. Covers all implemented systems, architecture, database schema, and development workflows.

## Core References

### D&D Rules
- **[SRD_CC_v5.2.1.md](SRD_CC_v5.2.1.md)** - D&D 5e System Reference Document
- **[SRD_TO_TALEKEEPER_MAPPING.md](SRD_TO_TALEKEEPER_MAPPING.md)** - How D&D SRD maps to TaleKeeper implementation

### Testing & Quality
- **[README_TESTING_FRAMEWORK.md](README_TESTING_FRAMEWORK.md)** - Qt6 testing framework guide
- **[CORE_REGRESSION.md](CORE_REGRESSION.md)** - Regression test suite documentation
- **[PIPER_TTS_SETUP.md](PIPER_TTS_SETUP.md)** - Text-to-speech setup instructions

### Monster Systems
- **[MONSTERS_README.md](MONSTERS_README.md)** - Monster database overview and usage
- **[MONSTERS_XML_GUIDE.md](MONSTERS_XML_GUIDE.md)** - Monster XML format specification
- **[MONSTER_UPDATE_SUMMARY.md](MONSTER_UPDATE_SUMMARY.md)** - Monster database update history

### Development Tools
- **[CLAUDE.md](CLAUDE.md)** - Development guide for working with this codebase
- **[TODO.md](TODO.md)** - Current development tasks and priorities
- **[function_catalog.md](function_catalog.md)** - Catalog of all functions in the codebase

## Analysis Reports

### Code Quality
- **[DEAD_CODE_ANALYSIS_REPORT.md](DEAD_CODE_ANALYSIS_REPORT.md)** - Dead code analysis
- **[OPTIMIZATION_REPORT.md](OPTIMIZATION_REPORT.md)** - Performance optimization analysis

### Bug Postmortems
- **[ACTION_CARD_VISIBILITY_BUG_POSTMORTEM.md](ACTION_CARD_VISIBILITY_BUG_POSTMORTEM.md)** - UI bug analysis and fix

### Import & Migration
- **[monster_comparison_summary.md](monster_comparison_summary.md)** - Monster data comparison
- **[monster_import_final_report.md](monster_import_final_report.md)** - Monster import final report

## Implementation Summaries

### Character Systems
- **[BAG_OF_HOLDING_SYSTEM.md](BAG_OF_HOLDING_SYSTEM.md)** - Bag of Holding implementation
- **[PROGRAMMATIC_CHARACTER_CREATION_SUMMARY.md](PROGRAMMATIC_CHARACTER_CREATION_SUMMARY.md)** - Programmatic character creation
- **[PROGRAMMATIC_CHARACTER_CREATION_ANALYSIS.md](PROGRAMMATIC_CHARACTER_CREATION_ANALYSIS.md)** - Character creation analysis
- **[PROGRAMMATIC_CHARACTER_TEST_RESULTS.md](PROGRAMMATIC_CHARACTER_TEST_RESULTS.md)** - Character creation test results

### Narrative & Content
- **[NARRATIVE_IMPLEMENTATION_STATUS.md](NARRATIVE_IMPLEMENTATION_STATUS.md)** - Narrative system status

## Art & Asset Generation

- **[lineart_lora_training.md](lineart_lora_training.md)** - AI art training for line art
- **[monster_art_generation.md](monster_art_generation.md)** - Monster art generation process
- **[humanoid_monster_image_status.md](humanoid_monster_image_status.md)** - Humanoid monster image status
- **[replacing_monster_images_manual.md](replacing_monster_images_manual.md)** - Manual image replacement guide

## Subdirectories

### development/
- **[INSTALLATION_COMPLETE.md](development/INSTALLATION_COMPLETE.md)** - Installation completion log
- **[RELEASE_NOTES_v3.0.md](development/RELEASE_NOTES_v3.0.md)** - Version 3.0 release notes

### reports/
- **[MONSTER_ATTACK_VALIDATION_REPORT.md](reports/MONSTER_ATTACK_VALIDATION_REPORT.md)** - Monster attack validation report
- **MONSTERS_SUMMARY.txt** - Monster database summary

---

## Documentation Organization

This documentation has been organized to separate:

1. **Implementation Documentation** - Consolidated into IMPLEMENTATION_GUIDE.md
2. **Reference Materials** - Setup guides, bug postmortems, SRD
3. **Analysis Reports** - Code quality, optimization, validation reports
4. **Asset Generation** - Art and content generation guides

All planning documents and obsolete implementation plans have been removed to reduce confusion between planned features and actual implementations.

For questions about the current implementation, start with IMPLEMENTATION_GUIDE.md.
