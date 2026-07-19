# Film Notes — clip `de906c40-RPReplay_Final1784292354.mp4`

Working notes for iterative tape analysis. **Observed** = visible in frames.
**Inferred** = reasoned from rules/context. Ambiguities flagged explicitly.

---

## Clip metadata (OBSERVED)

- Source file: `RPReplay_Final1784292354.mp4` (iOS ReplayKit screen recording).
- Video: 1206×658, 60 fps, 20.22 s, h264. Audio present (not yet analyzed).
- It is a **screen recording of a broadcast/stream** with graphics overlay.
- **Scoreboard (top-left):** "IQA WORLD CUP — RICHMOND, VA" logo → this is the
  **2023 IQA World Cup**, Richmond VA, July 2023 (~3 years before the 2026 request;
  matches "Team India 3y ago").
- Teams on scoreboard: **India 90 — Mexico 120**.
- **Score never changes across the whole clip** (India 90 / Mexico 120 from t=0.0 to
  t=20.2). → **No goal is confirmed during this clip.** (A goal could occur just after
  the clip ends, but not within frame.)
- **Game clock counts UP: 19:30 → 19:52.** The seeker floor is the first 20 min, so
  this is the **last ~30 s of the seeker floor**: NO seekers, NO flag runner in play.
  Pure chaser + beater play. (INFERRED from rules 3.4.3.)
- **Playback speed ≈ real-time (~1.1×).** Game clock advances ~22 s over 20.2 s of
  video. A "2× ▶▶" indicator flashes only in frame 0 → a brief press-and-hold
  fast-forward at the very start, then normal playback. Motion is real-time.
- **Ruleset caveat:** this is an **IQA 2023** match. My local rulebook is **USQ
  2025-26**. Core mechanics are shared, but specific numbers/timings may differ.
  Interpret rules with that caveat.

## Cameras / overlay (OBSERVED)

- **Main feed:** wide shot from one sideline. Far sideline (parked cars, bleachers,
  spectators, trees) fills the top ~1/3; pitch fills bottom ~2/3. Camera **pans
  left↔right to follow the ball**, so each end's hoops enter frame at different times.
- **PiP inset (top-right, blue border):** a **second, closer camera** at ground level
  near the near sideline. Mostly shows a referee walking + far-sideline background;
  occasionally catches a player close up (e.g. jersey #25). Useful for jersey detail.
- My extracted 2fps frames have a **yellow timestamp box top-left that overlaps the
  scoreboard** — read the scoreboard from clean crops of the original, not from the
  timestamped frames.

## Visual ID established for THIS clip (OBSERVED)

- **Team Teal:** mint / seafoam-green jersey, mostly white shorts.
- **Team Maroon:** maroon / dark-red jersey, mostly black shorts or leggings.
- Jersey numbers seen so far: maroon **#41**, maroon **#7 (?)**, a **#25** (teal, seen
  in PiP), teal **#10 (?)**. To be confirmed.
- **Referees:** black-and-white vertical stripes (multiple on pitch — head ref +
  assistants is normal). One ref in PiP wears a bucket hat + maroon shorts.
- **Balls:** an **orange dodgeball (bludger)** is visible in the central cluster in
  several frames. Quaffle (volleyball, lighter/white, larger) not yet reliably tracked.
- **Which team is India vs Mexico: NOT yet determined** — needs jersey crest/flag zoom
  or user confirmation. (Provisional guess to test: Mexico often plays in green →
  could be Team Teal; but unverified.)
- Headband colors (keeper=green, chaser=white, beater=black, seeker=yellow per rules)
  are at/below the resolution limit at this distance — will attempt on zoom, flag if
  not resolvable.

---

## PASS 1 — rough play-by-play (2 fps contact sheets) — PROVISIONAL

Times below are **my video timestamps** (t=…s); game clock in brackets.

- **t≈0.0–4.5s [19:30–19:37]:** Wide view near midfield. Both teams spread across the
  middle. A cluster of contested play left-of-center. An orange dodgeball visible
  center-left. Ball hard to track; play drifting slightly right.
- **t≈5.0–9.5s [19:37–19:42]:** Camera pans right. Play advances toward the **right-side
  hoops**. A teal ball-carrier appears to advance from left→center-right; players stream
  right. Looks like **Team Teal building an attack on the right-end hoops** (defended by
  Maroon). Orange dodgeball still in central area.
- **t≈10.0–14.5s [19:42–19:47]:** **Right-side hoops clearly in frame.** Attack develops
  into a **scrum/cluster around the right hoops** by ~13–14.5s. Multiple maroon players
  defending the hoop line; teal pressing. An orange dodgeball on the ground mid-field
  (~t=11s). This is the apparent climax of Phase 1. **No goal registered on scoreboard.**
- **t≈15.0–16.5s [19:47–19:49]:** **Transition.** View opens up; hoops now appear
  **center-left** with fewer players clustered and more open grass. Ball appears to move
  back leftward. Looks like **possession changed / ball cleared** — a likely **turnover**
  ending Teal's attack. (NEEDS ZOOM CONFIRMATION.)
- **t≈17.0–19.5s [19:49–19:52]:** Players build again toward the **left-side hoops**; a
  cluster forms near the left hoops by ~18.5–19.5s. Looks like **the other team (Maroon?)
  counterattacking the left-end (Teal's) hoops.** No goal within clip. A yellow-shirted
  person is on/near the field around t=17–18s (identity unclear — assistant ref? sub?).

### Provisional structure (INFERRED, to verify)
1. **Phase 1 (~0–15s):** Team Teal on offense, driving to the right-end hoops; Maroon
   defends. Ends with NO goal (~15s) — probable turnover.
2. **Phase 2 (~15–20s):** Counterattack the other direction toward the left-end hoops
   (probably Maroon on offense now). No goal within clip.

---

## KEY MOMENTS to zoom (Pass 2 targets)

- **M1 [~0–4s]:** Initial state — who holds the quaffle, team shape, attack direction.
- **M2 [~5–9s]:** The rightward advance — identify teal ball-carrier, any passes.
- **M3 [~10–14.5s]:** Right-hoop attack/scrum — shot attempt? beater beat? how it ends.
- **M4 [~14.5–16.5s]:** The transition/**turnover** — the single most important moment
  to resolve (did possession change, and how?).
- **M5 [~17–19.5s]:** Counterattack toward left hoops — who has the ball, shape.
- **Cross-cutting:** track the QUAFFLE and the **3 dodgeballs** throughout; identify
  **beaters** (ball-holders) and **keeper** (green headband, in keeper zone); read
  jersey crests to settle India-vs-Mexico.

## OPEN QUESTIONS after Pass 1
- Which color = India, which = Mexico? (crest/flag zoom or user)
- Is there a clear turnover at ~15s, or is it the same team re-attacking?
- Where is the quaffle at each phase? (not yet tracked frame-to-frame)
- Any beater knockouts ("back to hoops") that reshape the possession?
- Who/what is the yellow-shirted person at t≈17–18s?

---

## PASS 2 — dense zoom analysis (12 fps windows + high-zoom crops)

Extracted 12 fps windows (turnover t=13.0–16.5) and heavy crop+upscale strips
(pack-front, break-leaders lower band, origin t=8.5–12.5, start t=1–4, end t=16–20).
Times are my video timestamps.

### CORRECTIONS to Pass 1
- **Team colors refined:** "Team Teal" is actually **light / powder blue** (green cast
  came from grass reflection). Team B is **maroon**. Jersey numbers now legible:
  light-blue **#25** and **#17**; maroon **#41**.
- **India vs Mexico (still provisional, stronger now):** **light blue = INDIA**
  (blue is India's classic sporting color; #25/#17 are India), **maroon = MEXICO**
  (#41 is Mexico). No crest/flag was directly legible — CONFIRM WITH USER.
- **Direction re-anchored:** the pivotal motion is a **fast break toward frame-LEFT**
  (~t=13–16), NOT a "reset." Pass 1's "transition at 15s" is really the tail of this
  break. The right-of-center hoops seen through this window are **Mexico's hoops** (the
  end India was attacking); the break heads the other way toward India's end.
- **The quaffle IS trackable in close crops** (Pass 1 couldn't find it): it is a
  **light/white volleyball carried tucked under a player's arm**, distinct from the
  bright **orange dodgeball (bludger)**. This let me assign possession.

### What the zooms show (OBSERVED)
- **t≈0–8 [19:30–19:40]:** Contested, fairly settled play around **midfield**. Players
  spread; a **light-blue (India) beater holds the orange dodgeball** center-left; India
  #17 central. No frantic pack yet. Quaffle carrier not resolved here.
- **t≈8–11.5 [19:40–19:44]:** **India (light blue) attacks Mexico's hoops (right end).**
  The three hoops are clearly defended by a cluster of **maroon (Mexico)** players; India
  presses from the left/center. Origin-strip crops show India attackers driving at the
  hoop line. A **beater/bludger contest happens right at the hoops** (orange dodgeball;
  an India player leaps/reaches at the hoop ~t=11.5). At least one player is down/kneeling
  in the scramble (~t=10.5, center).
- **t≈11.5–13 [19:44–19:46]:** **Possession flips to Mexico at their own hoops.** Out of
  the hoop-line scramble, a **maroon player secures the white quaffle**; the orange
  dodgeball is carried out to the far left by a light-blue player. **Exact flip mechanism
  (keeper save / missed-shot rebound / interception / beat-forced drop) NOT resolvable** —
  the frames show a collapse of bodies at the hoop, then Mexico with the ball.
- **t≈13–16 [19:46–19:48]:** **Mexico fast-breaks toward frame-LEFT** (toward India's
  end). A **maroon chaser/keeper carries the quaffle tucked under-arm**, sprinting; a
  mixed pack of ~8–10 runs with them; **beaters from both teams battle over the orange
  dodgeball in the middle of the break**; 2–3 striped referees + a yellow-shirted official
  run alongside. India (light blue) chases back on defense.
- **t≈16–20 [19:48–19:52]:** The break reaches the **India end / midfield-left** and the
  pack **spreads out again** into more open play. **No goal** (scoreboard stays 90–120).
  Clip ends at game clock 19:52, still in the seeker floor.

### People/objects identified (OBSERVED)
- **India (light blue):** #17 (early, central), #25 (late, near camera).
- **Mexico (maroon):** #41 — **white headband → CHASER** (only clearly-read headband).
- **Balls:** 1 white quaffle (under-arm carry) + at least 1 orange dodgeball (bludger),
  actively contested. A green ball also glimpsed on the ground (2nd/3rd dodgeball) at far
  left ~t=11.5–12.5. The full 3-dodgeball state was not continuously tracked.
- **Officials:** 2–3 referees in black/white stripes on the pitch; **one person in a
  solid yellow shirt in the field of play** — during the seeker floor no seeker/flag
  runner is legal, so this is most likely an **assistant/field referee in a yellow
  officiating shirt** (INFERRED; flagged).

### Still unresolved after Pass 2 (footage-limited)
- Precise **turnover mechanism** at Mexico's hoops (~t=12).
- Any **knockout ("back to hoops")** event — beaters/bludgers are active but no clear
  quaffle-drop + dismount + hoop-tag was visible.
- **Headbands/positions** for nearly all players (resolution limit).
- **India-vs-Mexico jersey mapping** (strong inference, not proof) and the **yellow
  official's** exact role.
- Continuous **3-dodgeball / control** state (who held 2 of 3 when).
- Quaffle carrier during the **first ~8 s** (midfield phase).
