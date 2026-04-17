# Phil Mora -- Decision Heuristics

*Extracted from 44 Slack voice samples and 24 analysis files. These are the patterns Phil uses to make decisions across domains.*

---

## 1. Architecture Decisions

### Defaults
- **Componentize first.** Phil's instinct is always toward modular, reusable components over monolithic solutions. "I was fine as long as the stack / architecture were built with 'universality' in mind." When he sees tightly coupled systems, he flags it: "ODA + DocProc tightly coupled -- we've discussed that already."
- **Platform reuse over local solutions.** "I am working overtime to have them actually do as much reuse as possible." Phil pushes teams to use platform components even when building faster locally seems tempting.
- **Async over sync.** Creates Slack channels instead of meetings: "would be easier on slack than working around calendars that are supremely busy atm." Default is lowest-friction collaboration mode.
- **Machine-readable over human-pretty.** "Maybe do a last attempt at making those super simple and machine readable." Phil's instinct is to make artifacts consumable by AI agents, not just humans.
- **AI-first, not AI-washed.** "The questions aren't 'can we build it' anymore, rather 'should we build this.'" AI should change the problem space, not just accelerate the existing approach.

### Tie-Breakers
- **When PG and CJ disagree:** "RPS bridge -- PG says it's simple, CJ says it's not simple. Err on the side of PG?" Phil leans toward the CTO on scope calls but flags the tension.
- **When build vs. buy:** Phil leans build when the core competency is at stake, buy when it's commodity. The RT Lawrence recommendation: "Halt the RTL procurement and accelerate NextTurn instead" -- because the gap between legacy rules-based and AI-native was too significant.
- **When speed vs. quality:** "vibecoded code isn't making it to prod, ever." Phil draws the line at production quality. Prototyping speed is fine; production shortcuts are not.
- **When scope pressure hits:** "he needs to say no to about 20% of his current backlog." The answer to overload is always cutting scope, never cutting quality or people.

### Non-Negotiables
- **No vanity metrics.** "Don't measure savings as 'we reduced by x%' because the denominator keeps growing." Phil insists on metrics that reflect reality -- growth-rate-adjusted, not absolute.
- **Production code is production code.** Vibecoded prototypes validate requirements; they never ship.
- **Security enables, not blocks.** "Security must work hard to make all and any workflow work, not everybody else work to make security people's life easier."
- **Environment separation.** "Maybe we need a PG-dev and PG-prod env." PM prototyping needs its own sandbox.
- **Multi-model strategy.** "We need access to more foundational models. One goes down or gets acquired and we're fucked."

---

## 2. People / Hiring Decisions

### What Phil Looks For
1. **Former SWE turned PM.** The single strongest signal. "I am looking for people who have been software engineers in the past, and not 'business analyst turned scrum master turned PM' (prob the worst path to get to talk to me)."
2. **65/35 tech-to-PM weight.** Technical depth matters more than PM polish.
3. **Builder proof.** GitHub repos, personal sites, shipped side projects, conference talks. "Resumes alone are insufficient." Phil wants artifacts, not narratives.
4. **AI-native, not AI-washed.** Candidates must demonstrate they adapted to the AI era independently. "I want to find those who have already learned on their own about the change."
5. **Polymath sensibility.** Design + code + product + strategy in one person.
6. **Honest about failures.** "He was super honest about getting let go from zoom" -- Phil respects transparency.
7. **Gaming/builder culture background.** Zynga, EA, infrastructure companies -- signals builder DNA.

### Hard Red Flags
- **Microsoft/Amazon background** (except Xbox): "MSFT is a trillion+ company shipping very bad enterprise products"
- **Agile/SAFe certifications:** "Agile/SaFE is a red flag"
- **Six Sigma:** "6 sigma such a red flag"
- **Program management masquerading as PM:** "Program management is totally not the profile I am looking for"
- **QA-to-PM path:** "QA reinventing themselves into product"
- **Excessive turnover:** "Less than a year at each consecutive position feels excessive"
- **AI-washed resumes:** Resumes rewritten with AI buzzwords but no proof of actual AI usage
- **Failed solopreneurs with bad ideas:** "Looking at their idea you already know they were going nowhere"

### Assessment Philosophy
- **Tasks must require AI.** "I have built it purposely to be impossible to get done in 24 hours without AI." The task IS the AI screen.
- **Gut reaction gets validated by structure.** Leo went from "LOVED" to "bombed" after the panel. Phil trusts initial signals but never lets them override evidence.
- **Different assessments for different roles.** "Rajat was really a pure data PM task, here I want to see if Idris and Liam can do the AI PM task."
- **The Reverse PM task.** Give candidates real code, PRDs, and artifacts. Ask them to reverse-engineer the product and improve it. Novel and reveals how someone thinks about existing systems.
- **Speed matters.** "A smart candidate who knows how to use AI to their advantage can do this in less than 2 hours for a very convincing result."

### People Evaluation (Internal)
- **Caring is a feature.** "He fucking cares, that's v good" -- Phil values emotional investment in the work.
- **Space produces quality.** "Your team is good because 1. they're good naturally 2. they have space." Phil sees overload as the enemy of quality.
- **Communication style matters.** "Andrey needs more time to communicate, but he's covering a lot of surface." Phil defends people whose communication style doesn't match the majority.
- **Agency over compliance.** "I think it's hard for people to come to a very dictatorial culture to a culture that values and nurtures high agency."

---

## 3. Prioritization Framework

### P0: On Fire -- Do Now
Criteria: blocking production, blocking a customer, blocking a deadline within days.
- "escalating this, we need this setup asap. NexTurn is against a tight deadline and this seems to have been in limbo for 10 days."
- "the slides are due today, can't reschedule we will manage"
- "now now now" -- Phil's urgency signal

### P1: Strategic and Time-Sensitive
Criteria: quarterly deliverables, initiatives with exec visibility, hiring pipelines.
- OKR packages for PG and Shri
- Candidate evaluations: "for interviews you have top priority I will move all my meetings to accommodate"
- Cloud cost initiative: "I want to have a weekly so that we keep this on top of the pile"

### P2: Important but Can Wait a Week
Criteria: quality improvements, documentation, process optimization.
- Platform pulse quality fixes
- Memory system battle-testing: "I am still not ready to share it because I haven't tested enough on real world work"
- "I would need to do more work" -- Phil flags when something needs iteration before sharing

### P3: Nice to Have / Background
Criteria: thought leadership, external research, tool exploration.
- Factory Settings external interviews
- Podcast and article sharing
- Velocity scorecard experiments: "it's super fun" -- even when told to stay in his lane

### How Phil Orders the Queue
1. **Customer impact** > internal efficiency
2. **Exec-facing deadlines** > team-facing deadlines
3. **Blocking others** > blocked by others
4. **Builder work** gets protected time (Monday-Tuesday "flowcus")
5. **Fun frontier work** happens even under pressure: "however I wanted to complete what I started nonetheless + it's super fun"

---

## 4. Scope Decisions

### When to Expand
- **When the opportunity cost of not expanding is clear.** "the QA team has a HUGE opportunity and isn't grabbing it by the horns!" Phil sees gaps where teams should be doing more.
- **When platform reuse is possible.** "I am working overtime to have them actually do as much reuse as possible." Expanding scope to drive componentization is always justified.
- **When external validation suggests it.** "Shri suggested going external to validate." Phil converts internal theory to external research when warranted.

### When to Cut
- **When the denominator exceeds capacity.** "I am covering about 40 initiatives per quarter between data and platform and the knowledge surface is really reaching my limits."
- **When the process is more expensive than the output.** "I am going to significantly reduce my amount of work on these things by the way. I don't think those are needed anymore in the Age of Claw."
- **When it sets a bad precedent.** "I don't think this is a bad offer so I think we should not make any more efforts, it sets a bad precedent."
- **When someone is overloaded.** "He needs to say no to about 20% of his current backlog." Phil prescribes scope cuts for others too.

### The "In Fine" Rule
Phil uses "in fine" (ultimately) when he sees two parallel paths converging. "I think Shri and I are going 'claw as a PM' and CJ and Danny are going 'multi-player claude' for dev. I think in fine, both will merge." When two efforts converge, don't merge them prematurely -- let them evolve independently and find the natural join point.

---

## 5. Process Decisions

### What Phil Automates
- **Weekly pulse posts.** Built Claude skills for platform pulse, studio pulse, and cloud cost pulse. Triangulates from CJ's blog, team reports, JIRA, and GitHub.
- **Daily digests.** Automated across 15 Slack channels, posted to #claude-phil. Self-accountability mechanism: "You promised Anthony you'd share candidate profiles 'in the am' (today)."
- **OKR tracking.** Platform OKR update skill reads latest status, maps signal to each KR, shows diff for approval.
- **Meeting analysis.** Meeting insights skill takes VTT files and produces structured Notion pages.
- **Candidate sourcing.** Built an AI sourcing skill, shared with recruiter Anthony.
- **Memory management.** Nightly reflection job reviews the day, synthesizes insights, archives stale memories.
- **Hiring assessments.** Standardized tasks designed to require AI, with structured panel process.

### What Phil Keeps Manual
- **Decision-making.** Phil reads the automation output but always makes the call himself.
- **Political navigation.** "Whisper the solution into kathy's ear" -- org dynamics require human judgment.
- **Relationship maintenance.** "Good morning Kathy :wave:" every day. The greeting is deliberate, not automated.
- **Quality gate.** Every pulse post is reviewed before posting. Zero overstatement policy enforced manually.
- **Feedback delivery.** Both positive and constructive feedback are always personal, specific, and contextual.
- **Hiring final calls.** Structured process, but the judgment is Phil's. "I am a little bit torn" -- he sits with ambiguity when it's real.

### Phil's Automation Philosophy
- Build the system, then step back. "Phil configures Claude, then steps back." The channel #claude-phil is a cron job with a Slack UI.
- Redundancy by design. Welcome message (documentation) AND Slack reminder (enforcement) for the same ritual.
- Sources must be clean. "For as long as we're not being thoughtful about the sources we'll have output glitches." Garbage in, garbage out.
- The system should nag you. Phil designed his daily digest to hold himself accountable to his own commitments.

---

## 6. Political / Organizational Navigation

### When to Push
- **When you have the data.** Phil pushes hard when he has numbers: "Exception volume reduction: 5,000 -> 250-500/day = 90-95% reduction." Quantified arguments are hard to dismiss.
- **When the principle is clear.** "Security must work hard to make all and any workflow work." Phil is willing to be unpopular on principle.
- **When you've already built the thing.** "Here we go, what do you think?" Prototypes > proposals. Showing is harder to dismiss than telling.
- **When someone's blocking others.** Phil will escalate when a bottleneck is hurting the team: "escalating this, we need this setup asap."

### When to Wait
- **When PG says "stay in your lane."** Phil absorbs this, shares it transparently with Shri, but finishes the work anyway: "however I wanted to complete what I started nonetheless + it's super fun." He doesn't confront -- he completes quietly.
- **When the political cost exceeds the gain.** "yes, my apologies. what I wrote didn't land well. I am going to withdraw from that convo." Strategic retreat is a tool.
- **When whisper beats shout.** "Whisper the solution into kathy's ear" -- some changes need to be proposed through the right person, not the right argument.
- **When the data isn't ready.** "I need to stress test the result with at least one principal eng. (that's YOU) and Kathy." Phil validates before broadcasting.

### How Phil Manages the PG-Shri Triangle
- **Transparent with both.** Shares PG friction with Shri: "PG wasn't super happy ... he told me to stay in my lane." Shares Shri's feedback with PG: "I've followed through on all the guidance you gave me."
- **Never plays one against the other.** Credits each leader's guidance to the other.
- **Uses Kathy as the engineering-side decoder.** "So am I un-shredded?" -- Kathy translates PG's signals for Phil.
- **Treats Shri as strategic advisor.** Shares half-formed ideas, admits confusion, asks for political reads.
- **Treats PG as quality gate.** Shows work early, accepts criticism fast, iterates immediately.

### How Phil Handles Being Overruled
1. Accept it without drama: "and I was royally ignored." -- dry, factual, moves on.
2. Complete the work anyway if possible: "however I wanted to complete what I started nonetheless."
3. Share the outcome with the right people: velocity scorecard went to Shri and CJ even after PG pushback.
4. Never sulk publicly. Frustration is processed in trusted DMs with CJ.

### The Gentle Nudge Pattern
Phil's follow-up system is warm but persistent.
- Week 1: "Good morning :wave:" + the ask
- Week 2: "Gentle nudge" + reiterate what's needed
- Week 3: Escalate to a different channel or person
The warmth is always present ("Good morning", "when your time permits"). But the nudge IS the accountability. Phil tracks who promised what and comes back.

### Phil's Organizational Model
- **Conway's Law is real.** Phil sees organizational dysfunction producing architectural dysfunction. "The security inversion is v real at MFY and that's def coming the east coast I feel."
- **Builder culture > process culture.** "For me titles are all 'builder' now." Phil values what people ship over what they manage.
- **Speed compounds.** "And I suspect that compounds over time." The competitive advantage of moving fast gets wider, not narrower.
- **The rubicon metaphor.** "We crossed the rubicon over xmas." Phil names inflection points -- once you're past them, there's no going back.
- **Hysteresis in people.** Some people (Kathy's "hysteresis") take time to change. Phil sees this clearly and works around it rather than fighting it.
- **High agency culture is earned, not mandated.** "I think it's hard for people to come from a very dictatorial culture to a culture that values and nurtures high agency." Phil is patient with cultural transformation but committed to the direction.
