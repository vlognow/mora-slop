# Voice Corpus: #product-extended-staff (C0AE8P0JLJW)
# Source: Phil Mora (U099L4N8GAX)
# Channel: #product-extended-staff
# Time range: Oct 1, 2025 - Apr 17, 2026
# Harvested: 2026-04-14

---

## MSG-PES-001
- **timestamp:** 2026-04-15 11:43:31 EDT
- **thread:** reply
- **category:** CELEBRATION
- **context:** Welcoming Sarah Wilhoite-Johnson to the product org
- **text:** >
  plus plus! welcome Sarah! woo-oo!

## MSG-PES-002
- **timestamp:** 2026-04-14 12:47:47 EDT
- **thread:** standalone
- **category:** OPERATIONAL
- **context:** Flagging new engineering manager hire on Platform team
- **text:** >
  FYI. New EM on Platform ICYMI.

## MSG-PES-003
- **timestamp:** 2026-04-06 10:59:02 EDT
- **thread:** reply
- **category:** EXPLANATION
- **context:** Responding to Shri's comment about PRDs for agentic + human consumption -- Phil reveals he's been building a skill for this and references Karpathy's ideas on personal knowledge bases
- **text:** >
  yes, I have been writing a skill that does that -- I am still not ready to share it because I haven'd tested enough on real world work (audit comes to mind) however should be done this week. The karpathy post goes deeper in the concept of personal curated knowledge bases which I think makes a lot of sense as well.

## MSG-PES-004
- **timestamp:** 2026-04-04 16:31:48 EDT
- **thread:** standalone
- **category:** POSITION
- **context:** Provocative framing -- sharing tweet about idea files replacing PRDs
- **text:** >
  idea file = the new PRD???
  [tweet link]

## MSG-PES-005
- **timestamp:** 2026-04-02 11:55:41 EDT
- **thread:** standalone
- **category:** DIRECTION
- **context:** Pointing team to Claude Code /powerup starter kit
- **text:** >
  @here @Christopher Osufsen good morning
  if you are running claude 2.1.90, try this /powerup
  it's a neat "starter kit" of tutorials.

## MSG-PES-006
- **timestamp:** 2026-03-30 22:23:40 EDT
- **thread:** reply
- **category:** POSITION
- **context:** Caveat on the memory system -- it'll be obsoleted by Arya (next-gen agent)
- **text:** >
  A note: once we have Arya up and running this will be mostly obsolete

## MSG-PES-007
- **timestamp:** 2026-03-30 22:23:01 EDT
- **thread:** reply
- **category:** EXPLANATION
- **context:** Answering Shri's question about whether memory is stored locally -- explaining security considerations
- **text:** >
  yes -- it's local to your machine. If security allows it we could find a secure cloud location to store the memories. Now nothing is encrypted or linked to keys/secrets so I would need to do more work to get that cloud-ready.

## MSG-PES-008
- **timestamp:** 2026-03-30 22:21:13 EDT
- **thread:** reply
- **category:** DIRECTION
- **context:** Answering Shri's "how do I deploy it" question with installation instructions
- **text:** >
  you can ask claude to deploy it directly from the repo
  - It will install your memory.md and run a few python scripts for the mini database.
  - It will also install in all your skills and scheduled tasks
  - For your anthropic API key, generate yours in console.anthropic.com

## MSG-PES-009
- **timestamp:** 2026-03-30 22:16:23 EDT
- **thread:** standalone
- **category:** EXPLANATION
- **context:** Major pitch of the Permanent Memory system for Claude Code to the extended product team -- detailed technical description
- **text:** >
  Permanent Memory for Claude Code (I've been testing this, I could use more exposure to battle test it)

  Built a tool that gives Claude Code something it doesn't have natively -- persistent, agent-like memory. Think Claw's long-term context, but for Claude Code sessions and scheduled tasks. Memory survives across conversations, compounds over time, and self-organizes nightly.

  What it does:
  - SQLite full-text search across all memories (instant, free)
  - Semantic re-ranking via Haiku when keyword search isn't enough (~$0.001/query)
  - Every skill and recurring task logs what it learned -- context compounds over time
  - Nightly reflection job (Opus) reviews the day, synthesizes new insights, archives stale memories, flags contradictions
  - Focused context loading -- instead of dumping 200 lines of flat markdown, sessions get ~50 lines of what actually matters

  Why it matters:
  Claude Code forgets everything between sessions. MEMORY.md is a flat file that grows until it hits its limit. Claw agents get semi-permanent memory and context that persists -- but Claude Code doesn't. This bridges that gap. Memory is searchable, structured, and self-organizing. The nightly reflection means it gets smarter without manual curation -- closer to the always-on agent experience where Claude actually knows what happened yesterday.

  How it works:
  Single Python file, zero dependencies for core features. SQLite FTS5 with WAL mode for safe concurrent access. Every memory lives in both the DB (for search) and as a markdown file (for humans). Already wired into 9 automated skills -- platform pulse, daily digest, OKR updates, etc.

  Repo: [github link]

## MSG-PES-010
- **timestamp:** 2026-03-27 17:50:39 EDT
- **thread:** reply
- **category:** OPERATIONAL
- **context:** Telling Annette to list him as yes/yes in the AI tools canvas
- **text:** >
  @Annette Finstrom you can use me w yes/yes in the canvas table

## MSG-PES-011
- **timestamp:** 2026-03-27 13:40:43 EDT
- **thread:** reply
- **category:** DIRECTION
- **context:** Responding to Nick Tsueda about product repo access -- suggesting Mac + offering help
- **text:** >
  we are going to have a product repo on vlognow yes.
  My suggestion: get a mac and I will get you all the access you need

## MSG-PES-012
- **timestamp:** 2026-03-27 12:23:52 EDT
- **thread:** reply
- **category:** FEEDBACK
- **context:** Comprehensive feedback to Nick Tsueda on his multi-agent work, repo organization, Vercel site -- mixing praise with actionable suggestions
- **text:** >
  @Nick Tsueda
  - my suggestion would be for you to get a mac, also
  - Nice job on the multi agent investment thesis -- you could get a claw (securely) on an online bed (like hostinger), get a SoFi account with $10 in it and deploy a few agents to see how the investment is growing?
  - You did a v good job in org your repo on git, especially the "machine readable" part, I'd like to discuss w you how we could use git more at product team level
  - Like your Vercel site a lot, I've been using Framer and Claude (MCP) to revamp mine

## MSG-PES-013
- **timestamp:** 2026-03-12 13:39:39 EDT
- **thread:** reply
- **category:** DIRECTION
- **context:** Providing Claude Code install instructions and noting CC works in Windsurf too
- **text:** >
  for claude code install, the "official doc" is here [Notion link]. Pls DM me if you have issues.
  You can also use CC in Windsurf -- there is no difference in terms of model capabilities and context windows.

## MSG-PES-014
- **timestamp:** 2026-03-08 18:57:17 EDT
- **thread:** standalone
- **category:** POSITION
- **context:** Sharing Lenny's Podcast episode with Anthropic head of design
- **text:** >
  it's a good listen: [Apple Podcasts link]
  Jenny is the head of design at anthropic (ex figma)

## MSG-PES-015
- **timestamp:** 2026-03-05 19:45:08 EST
- **thread:** reply
- **category:** QUESTION
- **context:** Asking Chris if it's okay to add comments to his PRD template -- referencing his own conversation with Jake on the topic
- **text:** >
  thanks for sharing! okay to add comments if any? had an interesting discussion w Jake today on that topic !!!

## MSG-PES-016
- **timestamp:** 2026-03-04 15:42:17 EST
- **thread:** standalone
- **category:** CELEBRATION
- **context:** Praising Chris's presentation
- **text:** >
  Great Prez @Christopher Osufsen !!!

## MSG-PES-017
- **timestamp:** 2026-03-02 14:54:17 EST
- **thread:** standalone
- **category:** CELEBRATION
- **context:** Happy dance gif (celebration)
- **text:** >
  happy dance [giphy]

## MSG-PES-018
- **timestamp:** 2026-03-02 14:53:48 EST
- **thread:** standalone
- **category:** DIRECTION
- **context:** Announcing Claude Code + Slack plugin integration for product team
- **text:** >
  Quick Note: For those using Claude Code, you can now connect it to Slack
  - run /plugins on your terminal
  - search for "Slack"
  - Auth
  - Voila!

## MSG-PES-019
- **timestamp:** 2026-03-02 09:42:41 EST
- **thread:** reply
- **category:** SOCIAL
- **context:** Welcoming Nick Tsueda
- **text:** >
  Welcome @Nick Tsueda

## MSG-PES-020
- **timestamp:** 2026-02-19 15:10:28 EST
- **thread:** standalone
- **category:** EXPLANATION
- **context:** Pre-townhall message -- sharing framework, external research with 6 companies, Shri's talk transcription. Major structured communication.
- **text:** >
  Good afternoon!

  So tomorrow I'm presenting at townhall on AI and how we work. The basic idea is this: we can now build software 10x faster, but that's not actually the breakthrough. The real shift is that the bottleneck moved -- implementation is cheap now, but figuring out what to build is still expensive. We need to get way better at validation-first approaches.

  About a month ago I wrote up my thinking on this here: [Factory Settings Notion link]

  That document caused a bit of chaos in #VibeCoders which led to a really good conversation with Shri. He suggested I go validate these ideas with actual companies dealing with this AI shift, rather than just theorizing.

  So over the past 2 weeks I talked to 6 companies -- Meta, Intuit, Google, and 3 startups. Just asked them: how are you using AI day-to-day, what's working, what's not, what would you do differently?

  Huge thank you to Kamal, Ranjit, and Prasath for connecting me with some amazing startup CEOs. Seriously grateful for the intros -- the conversations were fantastic.

  I synthesized everything here: [External Case Studies Notion link]

  The results are really interesting -- and honestly pretty validating. The patterns I was seeing match what we're currently doing in Subro, COB, and Pharma, and what these teams are experiencing/doing.

  Also transcribed Shri's talk from the Product Onsite last week. It fits perfectly with all of this: [Shri's Ted Talk Notion link]

  Would love any feedback!

## MSG-PES-021
- **timestamp:** 2026-02-19 12:31:34 EST
- **thread:** standalone
- **category:** SOCIAL
- **context:** Bumping previous content
- **text:** >
  ICYMI

## MSG-PES-022
- **timestamp:** 2026-02-11 19:14:38 EST
- **thread:** standalone
- **category:** DIRECTION
- **context:** Sharing Windsurf/JupyterHub/SSH setup guide
- **text:** >
  [Notion setup guide link]

## MSG-PES-023
- **timestamp:** 2026-02-11 19:09:28 EST
- **thread:** standalone
- **category:** SOCIAL
- **context:** Sharing optionsmastery.ai link with Kamal, Ranjit, Prasath
- **text:** >
  @Kamal Sabnani @Ranjit Valasa @Prasath Chandrasekaran optionsmastery.ai

---

# Summary
- **Total Phil messages:** 23
- **Date range of Phil messages:** 2026-02-11 to 2026-04-15
- **Categories:** DIRECTION (6), EXPLANATION (4), POSITION (3), CELEBRATION (3), SOCIAL (3), OPERATIONAL (1), QUESTION (1), FEEDBACK (1)
- **Key themes:** AI tool evangelism, memory system pitch, Claude Code onboarding, external research validation, team welcoming, PRD evolution
