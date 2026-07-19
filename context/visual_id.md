# Quadball Visual Identification Guide (frame-by-frame, current era 2023–2026)

Practical guide for reading a single video frame of a current **quadball** match.

**Primary source:** *US Quadball Rulebook 2024, Version 1.0* (the 2024–25 USQ ruleset), held
locally at `/home/user/Srini/context/US_Quadball_Rulebook_2024_v1.0.pdf` (text: `rulebook.txt`)
and the official pitch diagram `/home/user/Srini/context/pitch_diagram_IMG_0453.png`. Section
numbers (§) refer to that rulebook. Headband colors, equipment, and hoop heights are consistent
across the current USQ / IQA / MLQ rulesets. Web items accessed 2026-07-17. Direct fetch of
usquadball.org / iqasport.org / mlquadball.com was blocked by egress policy on 2026-07-17, so the
local USQ 2024 rulebook is the authority; web search corroborates.

---

## 1. HEADBAND COLORS BY POSITION  ← the key identifier

Every in-play player wears a colored headband on the forehead (min ½ inch wide) that declares
their position. This is the single most reliable way to identify roles in a frame. [USQ §1.2.2,
§2.5.2–2.5.3]

| Color | Position | Count on pitch | Role |
|-------|----------|----------------|------|
| **White** | **Chaser** | 3 per team | Handle the Quadball/quaffle; score 10-pt goals |
| **Green** | **Keeper** | 1 per team | Goal defender; the 4th "chaser" |
| **Black** | **Beater** | 2 per team | Throw dodgeballs/bludgers to knock out opponents |
| **Yellow** | **Seeker** | 1 per team | Chase the flag runner; only present in the flag period |

Confirmed verbatim: keeper = green, other chasers = white (§1.2.2.A); beaters = black (§1.2.2.B);
seekers = yellow (§1.2.2.C); also USQ "How to Play," web 2026-07-17.

**Frame-reading tips:**
- A full side in play = **1 green + 3 white + 2 black** (= 4 chasers incl. keeper + 2 beaters),
  plus **1 yellow** seeker ONLY after the ~20-minute mark (flag period). Before then, no yellow on
  pitch. [§1.2.2, §3.4.3]
- **Jersey colors** distinguish the two TEAMS (same base color per team, must differ from opponent).
  A team's primary jersey color may **not** be yellow/gold (reserved for the flag runner) and may
  **not** be vertical black-and-white stripes (reserved for referees). [§2.5.2]
- Headband ≠ jersey. Read headband color for POSITION, jersey color/number for TEAM and player ID.
- Two players in the penalty box counts as "in play" for position totals, so a side may briefly
  show fewer than 6/7 on the pitch. [§9.4.3]

## 2. BALLS — telling the quaffle from the bludgers

Three ball TYPES are on the pitch; distinguish by **type/size and count**: [USQ §2.3]

- **Quaffle (the "Quadball")** — a **volleyball** (25.6–26.4 in circ.), slightly deflated. There is
  **exactly ONE.** Held/thrown only by **white/green** headbands. It is the object being shot at the
  hoops. [§2.3.1]
- **Bludgers (dodgeballs)** — **rubber dodgeballs** (8.5 in diameter), slightly deflated. There are
  **THREE.** Held/thrown only by **black** headbands. Smaller and rounder-looking than the
  volleyball; usually a different, solid color. [§2.3.2]
- **Flag** — a **tennis ball inside a fabric tail/sock** worn on the flag runner's lower back (see §5).
  Not carried by players. [§2.3.3]

**How to tell quaffle vs. bludger on video:**
- **Count and pattern:** one larger panelled volleyball (quaffle) vs. three smaller uniform rubber
  balls (bludgers). If a ball is in a white/green player's hands it's the quaffle; in a black
  player's hands it's a bludger.
- **Ball COLORS are NOT standardized** by the rulebook (it specifies size/material, not color) —
  **UNCERTAIN / event-dependent.** Do not identify a ball by color alone; use size, panelling
  (volleyball seams vs. plain rubber), and which position is holding it. [§2.3 — no color spec]
- A loose ball on the ground: a bludger goes **dead** the instant it hits the ground/out of bounds;
  the quaffle stays live on the ground. [§5.2.2, §7.5.2]

## 3. HOOPS — three per end, three heights

Each end has **three hoops standing on the goal line**, at three heights, hoop-loop inner diameter
**33 inches**. [USQ §2.2.2–2.2.3]

- Heights: **3 ft, 4.5 ft, and 6 ft.** [§2.2.2.A]
- The **6-ft (tallest) hoop is in the CENTER** of the goal line. [§2.2.3.A.i]
- The other two sit **3 yards** to either side of the center hoop. [§2.2.3.A.ii]
- **Left/right convention:** *facing a set of hoops from midfield,* the **3-ft hoop is on the LEFT**
  and the **4.5-ft hoop is on the RIGHT** (6-ft in the middle). This lets you orient a frame:
  identify the short vs. medium hoop and you know which way the camera faces that goal. [§2.2.3.A.iii]

**Frame-reading tips:**
- Reading which end is which: a team attacks ONE set of hoops for the whole game (chosen at coin
  toss). Combine hoop height order (short-tall-medium L→R from midfield) with jersey colors and
  play direction to locate the frame. [§3.1.2]
- The knockout "tag-in" point is the **center 6-ft hoop** — knocked-out players run to touch it, so
  clusters at the tall center hoop are players resetting. [§5.3.1.B]
- A hoop knocked over / loop touching the ground = **dislodged** and cannot be scored on until reset
  — useful if a shot appears to go in but no goal is signaled. [§4.3.1]

## 4. THE FLAG RUNNER / THE FLAG

- **Who:** a **neutral official dressed in yellow/gold**, NOT a member of either team; also acts as
  an on-pitch official. Their shorts/pants are all yellow or gold. [USQ §8.1.2, §10.1.9]
- **The flag:** a **tennis ball inside a fabric tail (sleeve), 10–12 in of visible tail,** attached
  to the **middle of the back** of the runner's shorts (like a flag-football flag at the rear
  waistband). [§2.3.3, §8.1.2]
- **When they appear:** only in the **flag period** — they enter during the 1-minute intermission
  after the ~20-minute seeker floor; before that, no yellow-clad runner is on the pitch. Once
  seekers are released they must **stay between the two keeper-zone lines** (i.e. the middle 24-yd
  band). [§3.4.4, §8.2]
- **On video:** yellow figure being chased by **two yellow-headband seekers**; a seeker grabbing at
  the runner's lower back = a **flag-pull (flag catch) attempt.** If the runner has any body part
  other than hands/feet on the ground = **"down"** and the flag is uncatchable. [§8.4.1]

## 5. BROOMS — mount vs. dismount

- Every in-play player keeps a **rigid plastic pole, 39–41 in long** (looks like a PVC pipe/broom)
  **between their legs.** It is NOT attached to them. [USQ §2.4.1, §5.1.1]
- **Mounted (in play):** broom (or the arm holding it) crosses the plane between the legs. [§5.1.1]
- **Dismounted:** the broom is no longer between the legs / lies flat on the ground with no hand on
  it. A player who becomes dismounted during play is **immediately knocked out.** On video: broom
  pulled out to the side or dropped, and the player breaking off from active play toward their
  hoops = they've been beaten/dismounted and are resetting. [§5.1.1–5.1.2]
- Players in the penalty box are **not** mounted (broom down). [§9.4.3]

## 6. REFEREE SIGNALS

Officials wear **black-and-white vertical stripes** (jerseys can't imitate this). [§2.5.2] The crew:
head referee (HR), lead + assistant referees (AR — dodgeball/off-ball), seeker/flag referee, goal
judges, plus scorekeeper/timekeeper. Only the **HR** issues cards. [§10.1]

**Confirmed signals & calls (from the rulebook):**
- **Good goal:** HR blows **one long whistle blast and raises BOTH arms.** (10 points.) [§4.1.1.C]
- **Stop play:** **paired short whistle blasts** (two quick tweets). [§3.3.1.A]
- **Restart / Quadball made live:** **one short whistle blast.** [§3.3.3.B, §4.2.2.C]
- **End of game (period final):** **three whistle blasts.** [§10.2.3]
- **Beat / knockout:** AR (or HR) makes the verbal **"beat"** call for a knocked-out player; a
  non-knockout hit is called **"safe"** or **"clear."** These are primarily **verbal** calls.
  [§5.2.4]
- **Delayed penalty (foul seen by a non-HR official):** that official **raises one hand** straight
  up and play continues; if the HR plays advantage on it, the HR also raises an arm. [§9.6.2]
- **Advantage:** HR **throws a marker** at the ball's location and **raises one hand straight up**,
  letting play continue. [§9.5.1.A.i]
- **Penalty cards:** HR **holds up the colored card** (blue / yellow / red) toward the fouling
  player and states the foul. Blue = 1 min & play down; Yellow = 1 min, 3rd yellow → red; Red =
  ejection + a sub serves 2 min. [§9.1.5, §9.4.1]
- **Reset used:** HR **loudly declares "reset used" and signals toward the offensive team's hoops.**
  [§7.4.3.E]
- **Other verbal calls:** "brooms down / ready / brooms up" (start), "remount" (restart), "ball out"
  (wrapped carrier released the ball), "boundary" (Quadball out of bounds), "back to hoops."
  [§3.2.1, §3.3.3, §6.3.1, §7.5.2]

**UNCERTAIN — could not confirm an exact hand signal:**
- **"No goal":** the rulebook confirms the *good-goal* signal (long whistle + both arms up) and
  references "no-goal calls" (§10.2.4) but does **not** specify a distinct no-goal hand gesture.
  In practice a waved-off / crossed-arms motion and simply the absence of the two-arm goal signal
  indicate no goal — **treat the exact no-goal gesture as UNCERTAIN.**
- The rulebook prescribes *what* officials call but generally not a codified hand-signal chart the
  way some sports do; many calls are **verbal**. Do not over-read specific arm gestures beyond the
  goal / advantage / delayed-penalty / card ones above.

## 7. PITCH MARKINGS — locating a frame

From the official USQ pitch diagram (`pitch_diagram_IMG_0453.png`) and §2.1: [USQ §2.1]

- **Pitch:** a **36-yd × 66-yd** rectangle (36-yd **endlines** at each hoop end; 66-yd **sidelines**
  along the length). Surrounding **player area** = **48 × 72 yd.** [§2.1.1, §2.1.9]
- **Midfield line:** across the middle, joining the sideline midpoints. **Four ball starting
  positions sit on it:** a dodgeball 6 yд either side of center, and a third dodgeball + the quaffle
  9 yд from center (side set by coin flip). A "center mark" marks midpoint. [§2.1.2, §2.1.6]
- **Keeper-zone lines:** two lines parallel to the endlines, **12 yд from the midfield line** on each
  side (so the middle band between them is 24 yд wide). Behind each keeper-zone line, toward that
  team's hoops, is the **keeper zone** (where that keeper is protected). This is the line the flag
  runner must stay between. [§2.1.3, §7.2.1]
- **Goal lines:** two lines **18 yд from the midfield line** on each side; **the three hoops stand on
  the goal line** (~15 yд inside the endline). [§2.1.4, §2.2.3]
- **Penalty boxes:** a 6×6-yд box just outside the sideline at the midfield line (scorekeeper's
  side), one per team — **look here for players sitting out / broom down.** [§2.1.5]
- **Substitution areas / benches:** long 21×3-yд strips outside the scorekeeper's sideline within
  each keeper zone. [§2.1.7–2.1.8]

**Frame-location shortcuts:**
- See hoops → you're near an end / keeper zone. See the dense midline with 4 ball spots → kickoff /
  "brooms up" formation, start of a period. [§3.2.1]
- Only the pitch boundary, midfield line, and keeper-zone lines are *required* to be marked; goal
  lines and ball spots are optional, so some fields won't show every line. [§2.1.10]
- Orient with the hoop-height rule (§3): short hoop on the left, medium on the right when you face a
  goal from midfield.

---

### Quick source-conflict / uncertainty flags
- **Ball colors:** NOT standardized — identify balls by size/type and by the holder's headband, not
  color. **UNCERTAIN.**
- **"No-goal" hand signal:** not codified in the rulebook — **UNCERTAIN**; good-goal (long whistle +
  both arms up) IS confirmed.
- **Flag value / seeker floor differ by ruleset:** flag = 35 pts [USQ/MLQ] vs 30 pts [IQA]; seeker
  floor = 20 min in all current rulesets (older "18 min" is outdated). Matters for reading the
  scoreboard, not the visuals. [§4.4.1, §3.4.3; web 2026-07-17]
- **Yellow on the pitch:** a yellow headband (seeker) or yellow-clad person (flag runner) only
  appears AFTER ~20 min — their presence dates the frame to the flag period.

---

## Referee signals — verified from rulebook + observed on tape (added 2026-07-17)

- **One arm held straight up in the air = ADVANTAGE / DELAYED PENALTY in progress.**
  An official saw a foul and is letting play continue; a marker may be thrown at the
  quaffle's location. Play will be stopped (and any card given) when the advantage abates
  — the fouling team gains the quaffle, a goal is scored for the fouled team, the fouled
  team stops trying to score, they commit their own foul, or the flag is caught.
  (USQ Rulebook §9.5.1 Calling Advantage; §9.6.2 Calling a Delayed Penalty — a non-head
  official "raises their hand and play continues as a delayed penalty," and if the head
  ref plays on, "they shall raise their own arm as well.")
  *Seen in Clip 1: a ref raised an arm during a hoop-line scramble for a suspected illegal
  tackle; play continued — the whole fast break happened under a played-on foul.*
- **Good goal = one long whistle + both arms raised.** (§4.1.1)
- **Quaffle-live after keeper restart = one short whistle.** (§4.2.2)
- Contact fouls to know the words for (§6): **wrap** (encircling an opponent with an arm),
  **tackle** (a wrap that brings a player to the ground), **charge** (forceful momentum
  contact with no wrap attempt). An "illegal tackle" = a tackle/wrap that breaks these
  rules (e.g. wrapping a player without the ball, or a wrap from behind with momentum).
