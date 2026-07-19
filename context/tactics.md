# Quadball Tactics & Strategy — Current Era (2023–2026)

Prepared for film analysis of a **chaser-focused possession**. Scope: how the real
sport of quadball (renamed from "quidditch" by the IQA in July 2022) is played and
coached **today**. Fantasy/Harry-Potter quidditch and the *Harry Potter: Quidditch
Champions* video game are ignored — several web searches surfaced that content as noise
and it was discarded.

---

## 0. Method, sourcing, and confidence notes (READ FIRST)

- **Primary authoritative source used**: the local **US Quadball Rulebook 2025–26 v1.0**
  (`/home/user/Srini/context/US_Quadball_Rulebook_2024_v1.0.pdf`; PDF metadata title is
  "Rulebook 25-26 v1.0", dated Oct 2025) and the **US Quadball Casebook 2024-25**. These
  give the *current* ruleset mechanics that shape tactics. Rule cites below (e.g.
  "USQ 7.2.2") point into this rulebook.
- **Web fetching was globally blocked in this environment.** `WebFetch` returned HTTP 403
  on every URL (including Wikipedia and example.com), and direct `curl` through the egress
  proxy was CONNECT-rejected (org policy) for governing-body sites
  (usquadball.org, mlquadball.com, iqasport.org) and several blogs
  (beyondthebig5.com, brainbound.blog, eighthman.com). **I therefore could not read the
  full text of any web source** — the web material below comes from **WebSearch-synthesized
  summaries** of those pages, not first-hand reading. Treat exact wording as paraphrase and
  the governing-body rule details for IQA/MLQ as **unverified** (see §10).
- **Date vetting.** Quadball tactical writing online is thin and much of the best analysis
  predates the 2022 rename. I mark each source's era. **Current-era (2023–26)** sources:
  the USQ 25-26 rulebook, Wikipedia "Quadball", and *Beyond the Big 5* (podcast/site actively
  covering quadball in 2024–25; its "Lurker's Guide to US Quadball Cup 2025" is April 2025).
  **Pre-rename "foundational" (2012–2020)** sources: The Eighth Man, SeekerPedia,
  From The Keeper Zone / UCR / Brandeis tumblrs, the Open Quidditch Coaching Library. The
  *core tactical concepts* in those (control, 1.5 bludgers, zone/man defense, iso, picks)
  are still the vocabulary of the game today, but **specific meta claims** ("every top team
  runs X") are dated and flagged where used.

---

## 1. Current-era terminology (important naming shift)

Under USQ/IQA rules the balls and roles were **formally renamed** at/after the 2022 rebrand,
though players and commentators still use the old words interchangeably:

| Current formal term (USQ rulebook) | Traditional / colloquial term still heard |
|---|---|
| **Quadball** (the scoring ball) | quaffle |
| **Dodgeball** (the disruptive balls) | bludger |
| **Flag** on a neutral **flag runner** | snitch / snitch runner |
| Quadball / dodgeball **control** | bludger control |

Source: USQ 25-26 rulebook Positions Overview; [Wikipedia — Quadball](https://en.wikipedia.org/wiki/Quadball);
[IQA name-change announcement](https://www.iqasport.org/news/iqa-announces-upcoming-change-of-quidditch-to-quadball/) (2022).
**When reading a possession, expect commentators to say either "quaffle" or "quadball" for the
scoring ball, and either "bludger" or "dodgeball" for the beater balls.** This doc uses
"quaffle/ball" and "bludger/dodgeball" as the more common spoken terms.

**Team on pitch (per side):** 4 chasers — one of whom is the **keeper** — plus 2 beaters,
plus 1 seeker (seeker enters only after the "seeker floor"). Chasers wear white headbands,
keeper green, beaters black, seeker yellow. Goals = 10 points; flag catch = 35 points under
USQ 25-26 (⚠ older/other sources say 30 — see §11). (USQ 25-26 Positions Overview.)

---

## 2. Rule mechanics that drive the tactics (USQ, current)

These are the levers every chaser/beater tactic below is built on. All are **USQ 25-26**
unless noted; most are effectively **ruleset-agnostic** in spirit across USQ/IQA/MLQ.

- **Drive = possession.** A team is the "offensive team" during its **drive**. A drive
  starts when they gain possession and **ends the instant the other team gains possession,
  a goal is scored, or the period ends** (USQ 7.3.1–7.3.2). Turnovers are therefore
  instantaneous offense/defense flips.
- **Knocking out & the knockout procedure.** Any player struck by an opponent's **live**
  dodgeball is "knocked out": they must **drop any ball, dismount, and run to touch the
  center (6-ft) hoop** before rejoining (USQ 5.2–5.3). This is why a single beat removes a
  chaser from the play for several seconds — the currency beaters trade in.
- **Live vs dead dodgeball (USQ 5.2.2).** A dodgeball only knocks players out while **live**
  — i.e., freshly propelled by a beater and not yet having hit the ground/a hoop base, gone
  out of bounds, been caught, or been stripped. **A thrown-and-missed dodgeball goes dead**
  and must be recovered before it can beat anyone again. This is the mechanical basis of
  "no-bludger" windows (§7).
- **Keeper zone & the "protected keeper" (USQ 7.2).** In their **own keeper zone** a keeper
  is a **protected keeper**: (a) immune to being knocked out by dodgeballs, and (b) has
  **indisputable possession** — opponents may not contact, steal, or interact with the ball
  they hold (USQ 7.2.2). **These powers switch off the moment any teammate holds the live
  ball outside the keeper zone, and come back when the drive ends** (7.2.2.B). This is the
  engine behind "keeper as safe launch point" and "keeper as 4th chaser" (§3).
- **Restrictor lines / "reset" (USQ 7.4.3).** The ball generally **cannot be moved backward**
  across a team's own keeper-zone line (hard restrictor) and may cross the **midfield line**
  backward only once per drive (a "**reset**"; ref calls "reset used"). A second reset, or
  going back over your own keeper-zone line, is an **illegal reset → turnover.** Limits how
  far offenses can retreat to re-set spacing.
- **Delay of game / stalling (USQ 7.4.1–7.4.2).** The ball carrier must advance at least at
  walking pace to midfield; offense must play "with the overall primary intent to score."
  A ball carrier held on the ground in contact with an opponent is a **stalled quaffle** —
  the ref counts down and, at zero, **turns the ball over to the defending keeper** in their
  keeper zone. Notably, a ball carrier is officially "**blocked**" (allowed to pause forward
  progress) by an opposing **beater holding a dodgeball within ~4 yards** — the rules
  themselves recognize the beater as the thing that stops a drive (7.4.1.C).
- **Out of bounds = turnover (USQ 7.5).** If a player carrying the ball goes out of bounds,
  the ball is **turned over** (7.5.1). A **live dodgeball that goes out of bounds instantly
  goes dead** (7.5.2.C) — another way beaters run out of live ammo. Play does **not** stop
  for a dodgeball going out.

---

## 3. CHASER PLAY (primary focus)

### 3.1 Offensive structure and roles
Offense is 4-on-4 in the quaffle game (3 chasers + keeper vs the same). Common role labels
(analogous to basketball; usage varies by team — treat as descriptive, not rigid):

- **Ball carrier / quaffle carrier** — the player currently holding the ball; primary
  decision-maker (drive vs pass). USQ requires them to keep advancing (§2 delay/stall).
- **Point chaser** — the chaser positioned "at the top" / central, typically the primary
  ball-handler and initiator of the set (like a point guard). Referenced as a distinct role
  in coaching materials and zone descriptions
  ([Open Quidditch Coaching Library](https://static1.squarespace.com/static/5e19b26c5920f22934dbe5c3/t/5e4a4187a4a90257d8d1b736/1581924752368/OPEN+Quidditch+Coaching+Library.pdf), ~2020;
  [Brainbound positions guide](https://brainbound.blog/quidditch-positions-guide)).
- **Wing chasers** — the chasers positioned wider/lower on the flanks who cut, receive
  cross-hoop passes, and finish; often the off-ball threats. (Same sources; ⚠ exact
  "point vs wing" nomenclature is not codified in the rulebook and differs between programs.)
- **Off-ball chasers** — any chaser without the ball; their job is spacing, setting picks,
  and timing cuts so a passing lane or an open hoop appears.
- **Keeper as a 4th chaser on offense** — the keeper "functions as a chaser with extra
  privileges" and routinely joins the attack. A common pattern: after conceding a goal or
  winning the ball, the **keeper brings the quaffle up from the zone and is "the tail-end of
  the offense," advancing then dishing to waiting chasers**, including to a chaser stationed
  **behind the opponents' hoops** ([Brandeis Quidditch — Keepers & Chasers](https://brandeisquidditch.tumblr.com/post/43096961162/basic-strategy-part-2-keepers-and-chasers), 2013, foundational).
  Because a protected keeper can't be beaten or tackled while in their own zone (§2), the
  keeper is the safest ball-handler to start a possession.

### 3.2 Using the keeper zone
The keeper zone is both a **safe harbor and a launch pad**: the protected keeper has
indisputable possession and dodgeball immunity there, so offenses **start/reset possessions
in the zone**, then push out ([MLQ/USQ how-to summaries]; USQ 7.2). But the **restrictor-line
rules** mean once the ball leaves the zone the offense cannot freely retreat back into it
(illegal reset → turnover, USQ 7.4.3), so the zone is a starting point more than a place to
stall. A stalled ball or several turnover types are also awarded to the **defending keeper in
their zone** (USQ 7.4.2), making the zone the reset hub for the *defense* too.

### 3.3 Driving vs passing
- **Driving** = the ball carrier attacks the hoops directly, trying to beat their defender
  and either score, draw a double team, or draw a beat. Skilled drivers "attempt to draw a
  double team or get penetration and space to set up bullet passes to other chasers"
  ([The Eighth Man](http://www.eighthman.com/), summarized).
- **Passing** = moving the ball to find an open shooter or a **cross-hoop pass** to a chaser
  on the far side / behind the hoops. Zones are specifically built to deny the cross-hoop
  pass (§4). Quick change-of-hands ball movement is a core offensive principle
  ([Quadball Australia — How Do You Play](https://quidditchaustralia.org/how-do-you-play)).
- The read is situational: drive when you have a numbers or bludger edge; pass to punish a
  collapsed/zone defense.

### 3.4 Named chaser actions (define each)
- **Give-and-go** — pass to a teammate then immediately cut (usually toward the hoops) to
  receive it back behind your defender. Explicitly taught as a callable play in coaching
  materials ([Open Quidditch Coaching Library](https://static1.squarespace.com/static/5e19b26c5920f22934dbe5c3/t/5e4a4187a4a90257d8d1b736/1581924752368/OPEN+Quidditch+Coaching+Library.pdf);
  [Quadball Canada — Dear Coaches](https://quidditchcanada.usetopscore.com/en_ca/p/dear-coaches-clueless-about-tactics)).
- **Handoff / handoff-and-drive** — a close exchange of the ball between adjacent chasers,
  optionally flowing straight into a drive by the receiver (same coaching sources).
- **Screen / pick (off-ball pick)** — a chaser bodies/blocks a defender to free a teammate.
  Coaching drills emphasize **off-ball picks**, and a distinctive pattern where the passer
  **"must immediately run to set another off-ball pick" after passing**, chaining picks for
  successive cutters (Open Quidditch Coaching Library, summarized). Analogous to a basketball
  screen; legality is governed by USQ contact rules (screens must be with legal contact).
- **Isolation / "iso" drive** — deliberately **clear out** teammates to give one strong
  driver a 1-on-1 against a single defender, then let them beat that defender to the hoops or
  draw help and kick out. (Concept is standard offense vocabulary; note the searchable
  quadball-specific write-ups on "iso" were thin — treat as ruleset-agnostic borrowed term,
  ⚠ lightly attested online.)

### 3.5 Fast break vs set offense
- **Fast break (transition offense)** — attack **before the defense is set**, immediately
  after a turnover or a conceded goal, exploiting a numbers edge (2-on-1, 3-on-2). The keeper
  or an intercepting chaser "can charge down the field before [the opponent] gets a chance to
  regroup" (Brandeis, foundational). See §8.
- **Set offense (half-court)** — a patient, structured possession run when the defense is
  organized; relies on ball movement, picks, and — critically — **bludger control** to remove
  the defense's beater threat before committing to a drive (§5–§7). Having control lets the
  offense "be more patient in running offenses, precise when passing, and take smarter shots
  on goal" ([From The Keeper Zone — Beaters on Offense](https://fromthekeeperzone.tumblr.com/post/38203867170/strategy-session-beaters-on-offense), 2012, foundational; concept still current).

---

## 4. DEFENSIVE structures

### 4.1 Man defense (a.k.a. "point"/man-to-man)
"The first defense you learn because it is the simplest: three chasers mark the three biggest
offensive threats … if their mark has the ball they cannot drive, and if their mark doesn't
have it they cannot receive it. The keeper guards the hoops … while keeping an eye on the
unmarked chaser." ([search-synthesized from Eighth Man / coaching materials]).
⚠ **Terminology flag:** the brief sometimes calls this **"point defense."** In quadball the
two standard families are **man** and **zone**; "point defense" is best read as a label for
**marking each offensive player ("point")**, i.e. man-to-man — but this exact phrase is
**not codified** and usage varies. Do not assume a commentator saying "point" means man
defense without context.

### 4.2 Zone defense (the modern default)
- **2-2 zone** — the workhorse. Two defenders split the hoop area (one guards the pass, one
  blocks the shot) while two defenders sit higher to stop drives; roles rotate so there are
  always "two on the goals and one on quaffle." A well-run 2-2 "eliminates the effectiveness
  of the attack on the hoops," is strong at goal-line defense, and makes **double-team
  tackles** more viable ([SeekerPedia — Defense: Keeper Zone](https://seekerpedia.wordpress.com/2016/12/30/defense-keeper-zone/), 2016, foundational).
- **2-keeper zone** — a keeper and a chaser take the **side hoops** to kill long-range shots
  while the other two chasers press forward horizontally to stop drives (SeekerPedia).
- **3-keeper / "Baylor" zone** — forces the offense to attack from the sides; a point chaser
  and beaters stand horizontally with the **keeper positioned behind the hoops** to react to
  passes over the top (SeekerPedia).
- **Why zone took over:** by ~2020, after skilled driver/receiver duos "killed" man defense,
  "every single top college team settled on some variation of the **2-2 zone** as their
  alternative scheme" ([The Eighth Man — How Two Athletes Killed Man D](http://www.eighthman.com/2020/03/16/how-two-athletes-killed-man-d-in-college-quidditch/), 2020).
  ⚠ That's a **2020** claim; zone remains standard vocabulary but exact current-meta
  prevalence isn't verifiable from the sources I could reach.

### 4.3 Hoop defense & the keeper's defensive role
- **Hoop defense** = the general job of protecting the three hoops: bodies between ball and
  hoops, denying the **cross-hoop pass**, and contesting shots. Zones concentrate defenders
  on the hoops so "with so many hands to intercept passes, it's hard to get a cross-goal pass
  to an open chaser" (SeekerPedia).
- **How chasers defend the hoops** — off-ball chasers guard cutters and the far hoop; on-ball
  chaser pushes the carrier **sideways away from the hoops** ("push them sideways … switch
  arms as the ball carrier switches directions," Open Quidditch Coaching Library).
- **Keeper on defense** — the last line: guards the hoops against the shot, covers the
  unmarked/open chaser, and — with the best sightline on the pitch — **quarterbacks the
  defense** ("yell when a teammate is about to be beat, call out the open chaser," Brandeis).
  Tackling is best used **1-on-1 or when a chaser is isolated with no pass** (Brandeis).

### 4.4 Doubling the ball carrier
Sending **two defenders at the ball carrier** to force a turnover or a rushed pass. Enabled
by zone spacing (double-team tackles "become more viable" in a 2-2, SeekerPedia). The classic
counter for the offense is to bait the double and hit the man it leaves open — which is
exactly what beat man defense (§4.2). Beaters can also "double" implicitly by forcing the
carrier to hesitate while a chaser closes.

---

## 5. BEATER PLAY & how it dictates chaser play

### 5.1 Control / bludger (dodgeball) advantage — the central concept
There are **2 beaters per team but only 3 dodgeballs**, so one team always holds **two**
dodgeballs and the other only one. **Holding two dodgeballs = "control"** (traditionally
"bludger control"; now also **"dodgeball control" / "dodgeball supremacy"**). "Having both
… confers a major advantage." ([Quadball Australia](https://quidditchaustralia.org/how-do-you-play);
[Wikipedia — Quadball](https://en.wikipedia.org/wiki/Quadball); The Eighth Man, foundational.)

**Why control matters (arithmetic of the beat):** a beater can only beat with a **live**
dodgeball, and a thrown-and-missed dodgeball goes **dead** (§2). The team with only one
dodgeball has a single "shot" of live-beat before that beater is disarmed and must recover a
ball. The team with two can beat, miss, and still have a live threat — so **the controlling
team can protect its drivers and pressure the opponent's chasers with impunity.**

### 5.2 What "having control" lets the OFFENSE do
When the offense also has control, it can "**mitigate the biggest variable**" and its plays
"start to work regularly … if they can control just one of the two beaters, they increase the
chances of success of their plays" ([Quadball Canada — Dear Coaches](https://quidditchcanada.usetopscore.com/en_ca/p/dear-coaches-clueless-about-tactics)).
Control lets the offense **be patient, pass precisely, and take smart shots** rather than
forcing (From The Keeper Zone). The offensive beater is "**a weapon to increase the
probability of the offense scoring**"; often the mere **threat to beat is enough** to freeze
the defensive beater and open a passing/shooting lane — you don't always have to actually
throw (From The Keeper Zone; UCR Quidditch).

### 5.3 Beaters defending the hoops & beating the driving ball carrier
On defense the beaters sit **near their hoops** as the last deterrent to a drive. The key
defensive-beater job is to **beat the driving ball carrier** at the moment they commit to the
hoops — recognized even in the rulebook, which treats a **beater holding a dodgeball within
~4 yards** as something that legitimately "blocks" a carrier's progress (USQ 7.4.1.C). A well-
timed beat on the driver ends the drive (knocked-out carrier must drop the ball, USQ 5.3).

### 5.4 The "bludger exchange"
The constant **economy of the dodgeballs**: because a thrown dodgeball goes dead and must be
retrieved, beaters continually **pass/hand dodgeballs to each other to stay "loaded,"** and
teams fight over the loose/dead ball to (re)claim control. In a defensive sequence, once the
offensive beater engages one defensive beater, that beater "**passes their bludger to the
other defensive beater, who can now make a play on the quaffle**" — the **exchange** keeps a
live dodgeball in the hands of whoever is best positioned to beat the driver (The Eighth Man,
foundational). ⚠ "Bludger exchange" is used loosely in the community both for this **passing
of the ball between beaters** and for a **trade of beats**; confirm from context.

### 5.5 The "1.5 bludger" strategy (offense with control)
The signature offensive-beater play. When your team **has control and is on offense**, one of
your beaters **leaves their dodgeball behind and goes up with the offense** specifically to
**neutralize the lone defensive beater** — creating a "**no-bludger opportunity**" for your
chasers. The offensive beater may **tackle/strip** the defensive beater to the ground, or
simply **scare them into throwing their one dodgeball** (which then goes dead), so "the goal
is to take the defense's dodgeball out of play to give the chasers as much time against
no-bludgers as possible." ([The Eighth Man — 1.5 Bludgers](http://www.eighthman.com/2014/11/12/1-5-bludgers-eliminating-the-sole-defensive-beater/), 2014;
reinforced by [Beyond the Big 5](https://www.beyondthebig5.com/articles/the-lurkers-guide-to-us-quadball-cup-2025), 2025.)
- **Defensive counter to 1.5:** the dodgeball-less defensive beater acts as a **human shield**
  in front of the beater who still holds the dodgeball — the offensive beater can't legally
  charge through the shield, so if the shield stays in front, the defensive beater keeps their
  dodgeball live and 1.5 fails (The Eighth Man). Alternatively a **chaser guarding the carrier
  can step into the offensive beater's lane** to shield their own defensive beater, buying
  time for the defensive beat on the carrier (From The Keeper Zone).

### 5.6 Engage beater vs free beater
A common two-beater division of labor: the **engage beater** focuses on beater-vs-beater
contact and applying pressure (contesting control, running the 1.5), while the **free beater**
plays off that — protecting space, covering the hoops, or making the play on the quaffle
(The Eighth Man, summarized).

### 5.7 "Beater line" — ⚠ weakly attested
The brief lists a "**beater line**." I could **not confirm** this as an established, defined
term in the reachable current sources (searches returned mostly fantasy noise). Best-guess
meaning consistent with usage: the **defensive beaters' positional line between the ball and
their own hoops** — the depth at which beaters hold to threaten any driver — analogous to a
defensive "line" in other sports. **Flagging as uncertain; verify against the specific
commentator/coach using it before relying on it.**

---

## 6. Beater roles summarized (offense vs defense)

- **Offensive beater:** protect your drivers, threaten/distract the enemy beaters, run 1.5 to
  manufacture no-bludger windows, and (only when needed) actually beat to regain control.
  "No need to actually beat the opposing beaters unless trying to regain control — the threat
  is enough" (From The Keeper Zone).
- **Defensive beater:** guard the hoops, **beat the driving carrier**, and defend control
  (shielding, exchanges). Losing control on defense is dangerous because it hands the offense
  a clean runway.

---

## 7. HOW BEATING AND CHASING INTERACT (the crux for reading a possession)

This is the single most important interplay to watch:

- **Offenses wait for a bludger to be "gone" before driving.** A drive into a live defensive
  dodgeball usually dies (the carrier gets beaten). So chasers **hold the drive until the
  defensive beat threat is neutralized.** The trigger is a **"no-bludger" situation**: the
  defensive beater(s) have **no live dodgeball** able to beat the driver — because it was
  thrown (now dead, being chased), knocked out of play, stripped, or the beater was
  neutralized by the offensive beater's 1.5.
- **Forcing / "drawing the beat."** Offenses actively **manufacture** that window: a chaser
  **feints or half-commits a drive to bait the defensive beater into throwing** their
  dodgeball. Once it's thrown (and misses/goes dead), the beater must chase it — and the
  offense **drives for real into the resulting no-bludger window.** Coaching materials
  explicitly teach chasers to "**draw the beat**" and to pass "until … the beaters make a
  mistake" (Open Quidditch Coaching Library).
- **No-bludger opportunity** (see §5.5) is the payoff state: the moment neither defensive
  beater can beat the driver, the offense presses its 4-on-4 quaffle advantage hard.
- **Reading cue:** *watch the dodgeballs before the ball.* Whether the offense drives or
  stalls is usually dictated by **who has control and whether a live defensive dodgeball is
  in position to beat the driver** — not by the chasers alone.

---

## 8. Transition, fast breaks & turnover dynamics

- **Instant flips.** Because a drive ends the moment the other team gains possession
  (USQ 7.3.1), a strip/interception **immediately** turns defense into offense — often before
  either team's beaters have re-sorted, which is when fast breaks and easy goals happen.
- **Sources of turnover to watch:** interception/strip; ball carrier or ball going **out of
  bounds** (USQ 7.5.1 — turnover); **stalled quaffle** (held on the ground in contact → count
  → ball to defending keeper, USQ 7.4.2); **illegal reset** (retreating too far → turnover,
  USQ 7.4.3); a **knockout beat** forcing the carrier to drop the ball (USQ 5.3).
- **Fast break (transition offense):** after a turnover or conceded goal, push the ball
  before the defense sets to exploit a numbers edge (2-on-1, 3-on-2). The keeper is a natural
  transition engine — bring it up from the zone and dish (Brandeis). ⚠ **Quadball-specific**
  transition write-ups are sparse online; searches mostly returned basketball transition
  theory (drive-and-kick, kick-ahead, score before defenders recover). Those principles map
  cleanly but are **borrowed analogies**, not cited quadball sources.
- **Dodgeball economy in transition:** the loose dead dodgeball after a beat, and dodgeballs
  going out of bounds (instantly dead, play doesn't stop — USQ 7.5.2), constantly reshuffle
  **control**; the team that scoops the loose dodgeball in transition often gets the runway.

---

## 9. Glossary (quick-reference, terms a commentator will use)

- **Quadball / quaffle** — the scoring ball; goals worth 10.
- **Dodgeball / bludger** — beater balls; a live one knocks players out.
- **Control (bludger/dodgeball control, "supremacy")** — holding **2 of 3** dodgeballs; a
  major advantage.
- **No-bludger / no-bludger opportunity** — a moment when the defense has **no live dodgeball**
  able to beat the driver; the green light to drive.
- **1.5 bludgers / 1.5 strategy** — offensive beater leaves their ball and goes up to
  neutralize the lone defensive beater, manufacturing a no-bludger window.
- **Drawing/forcing the beat** — baiting the defensive beater to throw so the offense can
  drive into the dead-ball window.
- **Live / dead dodgeball** — live can knock out; a thrown-and-missed or OOB dodgeball is dead.
- **Beat** — hitting an opponent with a live dodgeball (knockout).
- **Bludger exchange** — beaters passing dodgeballs between themselves to stay "loaded" / the
  scramble over the loose ball (⚠ also used for a trade of beats).
- **Engage beater / free beater** — pressure/contact beater vs the off-ball support beater.
- **Beater line** — (⚠ uncertain) the defensive beaters' holding line between ball and hoops.
- **Protected keeper / keeper zone** — keeper in own zone: dodgeball-immune + untouchable
  possession; powers drop when a teammate takes the ball out of the zone, return at drive end.
- **Drive** — a team's possession; also "a drive" = a chaser attacking the hoops.
- **Point chaser / wing chaser** — top/initiator vs wide/finisher chaser roles (informal).
- **Iso** — clearing out to give one driver a 1-on-1.
- **Give-and-go / handoff / off-ball pick (screen)** — chaser actions to free a scorer.
- **Cross-hoop pass** — a pass across the front of the hoops to an open far-side chaser;
  the shot zones are built to stop.
- **Reset** — legally moving the ball backward over midfield once per drive; a 2nd = turnover.
- **Stall / stalled quaffle** — carrier pinned on the ground → count → turnover to keeper.
- **2-2 zone / 2-keeper zone / 3-keeper (Baylor) zone** — the main zone-defense shapes.
- **Man / "point" defense** — marking each offensive player (⚠ "point defense" label varies).
- **Doubling** — two defenders collapsing on the ball carrier.
- **Brooms up** — the referee's start call; players sprint for the balls at midfield.

---

## 10. Ruleset attribution (agnostic vs USQ/IQA/MLQ)

- **Ruleset-agnostic** (true across USQ, IQA, and MLQ as far as reachable sources show):
  4 chasers incl. keeper + 2 beaters + 1 seeker; 3 dodgeballs → **control** dynamics; keeper
  zone with a protected keeper; 10-pt goals; and therefore essentially all of the **chaser**
  and **beater** *tactics* above (control, 1.5 bludgers, no-bludger, iso, give-and-go, picks,
  man vs zone, hoop defense, doubling, drawing the beat). These are strategy, not rules-text,
  and travel across leagues.
- **USQ-specific mechanics (from the 25-26 rulebook)** that shape but don't rename the tactics:
  **restrictor lines / one "reset" per drive**, the **stalled-quaffle** countdown to a keeper
  turnover, the **delay-of-game "blocked by a beater within ~4 yards"** definition, and
  **flag = 35 points**. These particular thresholds are what I can *verify*.
- **IQA & MLQ:** I **could not access** iqasport.org or mlquadball.com (egress-blocked), so I
  **cannot verify** their current rulebooks' exact numbers (e.g., flag/seeker point value,
  reset/stall specifics, any timing differences). Historically MLQ has run its own rulebook
  variant. **Treat any USQ threshold above as USQ-only until IQA/MLQ text is checked.**
  (Search did surface an [IQA Rulebook 2024 PDF](https://www.iqasport.org/wp-content/uploads/2024/08/IQARulebook2024.pdf)
  and MLQ rules pages — currently unreachable here.)

---

## 11. Conflicts & uncertainties (flagged, not merged)

1. **Ball naming.** Formal USQ term is "**Quadball**" (ball) / "**dodgeball**"; most
   players/commentators still say "**quaffle**"/"**bludger**." Both appear in current sources.
   Not an error either way — a register difference.
2. **Flag/seeker point value.** USQ 25-26 rulebook states **35 points** for the flag catch;
   older and some general-reference sources (and fantasy) say **30**. Likely a rules change
   and/or league difference — **verify per league**. (Peripheral to chaser analysis.)
3. **"Point defense" = man defense?** The brief pairs them. In quadball the codified split is
   **man vs zone**; "point defense" is not a standardized term in the sources I could reach.
   Read it as "marking each player" but confirm from context. **Flagged, not assumed.**
4. **"Beater line."** Not confirmed as a defined term (see §5.7). **Uncertain.**
5. **"Bludger exchange."** Used for both *passing the ball between beaters* and *a trade of
   beats*. **Confirm from context.**
6. **Zone-vs-man meta.** "Everyone runs 2-2 zone" is a **2020** Eighth Man claim; still the
   default vocabulary but current prevalence is unverified from reachable sources.
7. **Transition/fast-break specifics** for quadball are **thinly documented online**; §8
   leans on rule mechanics + borrowed basketball principles, explicitly flagged.
8. **Source reading limitation.** All web content here is **WebSearch-synthesized**, not
   first-hand page reads (WebFetch/curl blocked). Governing-body and blog specifics should be
   re-verified against the primary pages if precision matters.

---

## 12. Sources (with era / date reliability)

**Current-era (2023–2026) — higher confidence:**
- US Quadball **Rulebook 2025–26 v1.0** (local PDF, Oct 2025) — authoritative current ruleset.
- US Quadball **Casebook 2024-25** (local PDF).
- [Wikipedia — Quadball](https://en.wikipedia.org/wiki/Quadball) — current terminology, control, keeper zone.
- [Beyond the Big 5 — The Lurker's Guide to US Quadball Cup 2025](https://www.beyondthebig5.com/articles/the-lurkers-guide-to-us-quadball-cup-2025) — Apr 2025; 1.5 strategy, current competitive context. (Reached via search summary only.)
- [IQA — "Announces Upcoming Change of Quidditch to Quadball"](https://www.iqasport.org/news/iqa-announces-upcoming-change-of-quidditch-to-quadball/) — 2022 rename. (Unreachable directly.)
- [US Quadball — Play Quadball / how-to](https://www.usquadball.org/how-to-play) — current overview. (Unreachable directly.)
- [Major League Quadball — What is Quadball](https://www.mlquadball.com/what-is-quadball) — current overview. (Unreachable directly.)
- [Quadball Australia — How Do You Play](https://quidditchaustralia.org/how-do-you-play) — current national-body overview.

**Pre-rename foundational (2012–2020) — concepts still current; meta claims dated:**
- [The Eighth Man — 1.5 Bludgers: Eliminating the Sole Defensive Beater](http://www.eighthman.com/2014/11/12/1-5-bludgers-eliminating-the-sole-defensive-beater/) — 2014.
- [The Eighth Man — How Two Athletes Killed Man D in College Quidditch](http://www.eighthman.com/2020/03/16/how-two-athletes-killed-man-d-in-college-quidditch/) — 2020 (man→2-2 zone shift).
- [The Eighth Man — beater strategy tag](http://www.eighthman.com/tag/beater-strategy/) — engage/free beater, exchange.
- [SeekerPedia — Defense: Keeper Zone](https://seekerpedia.wordpress.com/2016/12/30/defense-keeper-zone/) — 2016; 2-2 / 2-keeper / 3-keeper(Baylor) zones.
- [From The Keeper Zone — Strategy Session: Beaters on Offense](https://fromthekeeperzone.tumblr.com/post/38203867170/strategy-session-beaters-on-offense) — 2012; offensive beating, threat-to-beat.
- [UCR Quidditch — Beaters on Offense](https://ucrquidditch.tumblr.com/post/38261598009/strategy-session-beaters-on-offense) — 2012 (companion).
- [Brandeis Quidditch — Basic Strategy Pt 2: Keepers & Chasers](https://brandeisquidditch.tumblr.com/post/43096961162/basic-strategy-part-2-keepers-and-chasers) — 2013; keeper-as-4th-chaser, defensive quarterbacking.
- [Open Quidditch Coaching Library (PDF)](https://static1.squarespace.com/static/5e19b26c5920f22934dbe5c3/t/5e4a4187a4a90257d8d1b736/1581924752368/OPEN+Quidditch+Coaching+Library.pdf) — ~2020; give-and-go, off-ball picks, "draw the beat," ball-carrier defense.
- [Quadball Canada — Dear Coaches: Clueless About Tactics](https://quidditchcanada.usetopscore.com/en_ca/p/dear-coaches-clueless-about-tactics) — callable plays, controlling one beater.
- [Brainbound — Quidditch Positions Explained](https://brainbound.blog/quidditch-positions-guide) — positional roles (date unclear; uses "quadball", so post-2022). (Reached via search summary only; anti-bot blocked.)

*All web sources were accessed via WebSearch-synthesized summaries on 2026-07-17; direct page
fetching was blocked in this environment. Local USQ PDFs were read directly.*
