# Hack Club submission status

Checked against the current Hack Club Blueprint submission guidelines and design-review checklist on **2026-08-27**.

The public Blueprint landing page currently says that its program ended on **March 31, 2026**. Confirm which active Hack Club program or reopened submission portal you are using before relying on this checklist; the repository structure below follows Blueprint's published shipping requirements.

## Ready in this repository

- [x] Root README with description, motivation, intended use and build overview
- [x] PCB screenshots and a PCB 3D render
- [x] BOM table at the end of the README
- [x] Root `BOM.csv` with estimates, sources and part notes
- [x] Editable KiCad schematic and PCB sources
- [x] Gerber ZIP, JLC BOM and corrected CPL
- [x] PCB STEP export
- [x] Off-board wiring and assembly plan
- [x] Dated multi-session journal with images and time accounting
- [x] Detailed engineering history, including mistakes and fixes
- [x] Production audit reports and checksums

## Blocking a truthful final submission

- [ ] **Complete enclosure CAD:** `CAD/walkiepcb_revE.step` is a PCB export, not a full enclosure assembly. Blueprint requires the editable enclosure source and full-assembly STEP for a project that needs a case.
- [ ] **Application firmware:** the board requires custom ESP32 firmware. A status note or blink example does not satisfy the voice-radio requirement.
- [ ] **Physical prototype evidence:** no assembled board has been powered, programmed, acoustically tested or range-tested yet.
- [ ] **Final external-part sourcing:** select exact potentiometer, power switch, enclosure material and any battery/antenna substitutions, then replace the remaining generic/TBD BOM rows.
- [ ] **Author-written journal/README review:** Blueprint prohibits AI-generated README and journal content. The current files are a transparent reconstruction from project records and must be reviewed and rewritten by the author in their own words before submission.
- [ ] **Sanity check by another person:** record who reviewed the design and what feedback was addressed.
- [ ] **Commit and push the files:** the prepared repository changes are currently local/untracked. Hack Club's portal checks the GitHub repository, so it cannot see these files until the author reviews, commits and pushes them.

## Recommended submission sequence

1. Finish the enclosure model and commit the editable CAD plus full STEP assembly.
2. Implement at least the complete intended firmware path: controls, display, battery monitoring, I2S capture/playback, codec, SX1262 transport and push-to-talk state machine.
3. Order and assemble the smallest prototype batch.
4. Add real build photographs and measured test results to the README and new journal entries.
5. Update the BOM with actual checkout prices and final purchase links.
6. Rewrite the reconstructed README/journal in the author's own voice.
7. Push the repository and enter the same dated sessions in the Hack Club journal UI.

Official references used for this audit:

- [Hack Club Blueprint submission guidelines](https://github.com/hackclub/blueprint/blob/main/docs/about/submission-guidelines.md)
- [Hack Club Blueprint design-review checklist](https://github.com/hackclub/blueprint/blob/main/docs/ai_reviewer_guide_design.md)
- [Hack Club: What is shipping?](https://github.com/hackclub/blueprint/blob/main/docs/resources/shipping.md)
