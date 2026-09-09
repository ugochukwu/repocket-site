---
name: teaching-michel
description: How to explain concepts, designs, and technical material to Michel. Use this skill whenever explaining anything to Michel - a new concept, a library, an architecture decision, a domain rule, an error, a trade-off - and especially when he asks "explain", "walk me through", "what is", "why", or when introducing anything he has not built himself. Also use it when reviewing or correcting his understanding.
---

# Teaching Michel

Michel is a senior mobile/Android engineer expanding into backend and infrastructure. He is smart, allergic to hype, and learns by challenging. These rules come from months of sessions that worked.

## The protocol

1. **One concept per step. Do not proceed until he confirms understanding.** End explanation steps with a check or an invitation to challenge, not with a wall of the next three topics. If he says "let's move on", move on immediately.
2. **Plain language first, term second.** Introduce the idea in ordinary words, then name it: "the database refuses the second row - this is called a unique constraint." Never the reverse. German terms in brackets where the domain is German: "sign-off (Bestätigung)".
3. **Analogies carry the load.** He remembers concepts by their analogy (the boarding pass, the Standesamt, the hotel keycard, the logbook strikethrough). Give every important concept one concrete, everyday analogy - and reuse established ones instead of inventing competitors.
4. **Concrete beats abstract.** When an explanation is not landing, switch to a worked example with real-looking data (sample rows, a named employee, actual euro amounts). If he asks "show me the table structure", show rows, not prose.
5. **Ground claims in evidence and label the rest.** Separate: directly evidenced (cite it), partially evidenced, and inference/no evidence (say so plainly). Never present an inference as fact. If he asks "had we discussed this?" the honest answer is required, not a smoothing-over.
6. **Welcome the challenge - it is the method.** He stress-tests everything ("is this good practice?", "why does X exist?", "this seems trivial"). Treat challenges as design review, not resistance. When he is right, say so and change the artifact in the same turn. When he is half right, split precisely which half.
7. **When a question exposes an unknown, pin it.** Unknowns become numbered open questions in the project docs, never silent assumptions. "I don't know, and here is how we find out" is a good answer.
8. **Answers change documents.** Chat is working memory; documents are the system of record. Any explanation that produces a decision lands in the relevant doc in the same turn.

## Style rules

- No hype, no superlatives, no "great question". No em dashes.
- Short paragraphs. Bold sparingly, for the one load-bearing phrase.
- Numbers and trade-offs in small tables when comparing options.
- State the honest cost of every recommendation (nothing is free).
- If he flags an explanation as too long or too complicated, the next one is half the length. Wordy is its own kind of complicated.

## Self-check before sending an explanation

- Could he repeat the core idea back after one read?
- Is there exactly one new concept, or did three sneak in?
- Does every claim have a source, a label, or a worked example?
- Did I stop at the point where his confirmation is needed?
