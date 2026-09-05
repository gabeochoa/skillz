---
name: value-oriented-programming
description: "Tony Van Eerd's value-oriented programming, as working heuristics. Use when writing or reviewing C++ that involves designing a class, deciding member vs free function, choosing what a function takes and returns, splitting a long function, or untangling code that shares mutable state. Also for 'is this a value or an object', 'should this be a member', 'why is this class so hard to change'."
---

# Value-oriented programming

Distilled from Tony Van Eerd's two C++Now talks: *You Say You Want to Write a
Function* (Part 1, 2023) and *Return of the Values* (Part V, 2024). His framing,
applied as decision rules. Sources are transcripts, not slides, so the phrasings
are his and the examples are reconstructed.

**The problem being solved is entanglement.** Not object-orientation, not
performance, not style. Code that cannot be reasoned about locally, and state
that changes here because something changed over there. Every rule below exists
to keep pieces of code separate.

## Complecting, and why bad code is the default

`complect` (Rich Hickey): from Latin *plecto*, to fold or braid. Simple = one
fold. Complex = many folds. *Easy* comes from adjacent — close at hand.

The trap is that **complecting is easy**. At almost every step, the cheapest
action makes the code worse. Adding an `if` is easier than extracting a
function. Reusing the parameter you already have is easier than adding the one
you need. Putting the new field on the existing class is easier than asking
where it belongs. Code rots one locally-reasonable step at a time.

So the counter-move is not cleverness, it is noticing that the easy step is the
wrong one. Van Eerd's own summary of his talks: he wants you to steal short
phrases you can say out loud in review. "Separate calculating from doing."
"Classes are made of velcro." "Dog in the fridge."

## Functions

**Write the function you want to see in the world.** Functions are answers to
questions. If you catch yourself thinking "this would be easy if I had X", the
move is to write X, not to inline it. It does not exist *yet*.

This is about **shape, not speculation**, and that is where it meets YAGNI. Do
not invent functions for capability nobody has asked for. But when you are
already writing the code, extracting the function it is asking for costs
nothing — Van Eerd's point is precisely that the good version was never harder
to write, only slightly less immediate. YAGNI governs whether the capability
exists; this governs what it looks like once it does.

**Top-down on the way down, bottom-up on the way back up.** You write
`is_facing_north(projector)` because that was your question. Then you look at
the body and it only touches `orientation` and `tolerance`. Now go back up and
change the signature. Most people do the first half and skip the second, which
is how every function ends up taking the whole world.

**Don't pass the fridge when the dog only wants what's in it.** If the first
line of a function digs one or two fields out of a big parameter, those fields
were the real parameters. Passing the big thing hands the callee access to
everything reachable from it, and someone will eventually use that access for a
locally-good reason.

**Separate calculating from doing** (Eric Normand, *Grokking Simplicity*). Van
Eerd calls this the rule that never fails him. A function that computes
something and then stores it is two functions. Split them, return the value, and
let the caller do the storing. This is what makes the code testable, reusable,
threadable, and re-runnable with different inputs — the last one is usually what
you discover you needed.

**Returning `void` is a code smell — with one architectural exception.** A big
`void` function usually contains a pure function hiding inside a class, plus one
line of mutation at the end. That is the case worth splitting.

The exception: where the architecture makes *doing* the whole job, void is
correct and the rule is noise. An ECS system, a render pass, a command handler —
these exist to mutate. Do not flag them. Do flag the 150-line void helper they
call, because that is the pure function in disguise.

**Prefer returning to out-parameters.** `auto v = f(x)` tells you what happened;
`f(x, v)` makes you go read `f` to find out whether it clears, appends, or
touches globals. Move semantics mean the cost argument is mostly gone. When the
in-out version genuinely wins (reusing capacity in a loop), keep both and give
the out-param one the uglier name.

## Member or free?

**Classes are made of velcro.** Every function you attach makes the class
heavier and widens the blast radius of every change to it.

Default to **free functions**. Reasons, in order of force:

1. A free function *cannot* break the class's invariants. A member can, even
   momentarily.
2. A member function is tied to the representation. Change `orientation` from
   Euler angles to quaternions and every member has to be revisited; the free
   function that goes through the public API does not.
3. Non-member non-friend functions improve encapsulation (Scott Meyers, 2000 —
   this is not new).
4. There are infinitely many useful functions over a type. Note that we do not
   put them all on `std::string`, which settles the principle.

Keep on the class only the **basis set**: the smallest group that needs access
to the representation, plus any function that turns O(n²) into O(n) by reaching
inside. Everything else lives outside, in a `<type>_utils` header if need be.

## Value or object?

**Object**: has identity, lives at an address, changes over time, is observed
and referenced, is usually not copyable. Buttons. Physical devices. The document
root.

**Value**: `int` is the canonical one. Copyable, comparable, substitutable.
Nobody cares where it lives, only what it is.

Van Eerd's test for **regular** (Stepanov, 1998):

```cpp
T b = a;                 // copy
assert(a == b);          // copies are equal
assert(a == a);          // and equal to themselves
T c = b; assert(c == a); // transitive
a = something_else;
assert(b == c && b != a); // changing a must not touch b or c
```

That last line is the whole point. "Copy or copy not, there is no shallow."

**Why objects go wrong**, two mechanisms:

- **Nexus of complecting.** Everything about a camera goes on the camera class,
  including the three masks and the intermediate images that should have been
  locals. Half the fields are invalid half the time. Now touching one concern
  breaks another.
- **Graph of references.** Objects have stable addresses, so you can point at
  them, so you do. `A` holds an `X` and `B` holds the same `X` — you did not
  design that structure, you fell into it. Sean Parent calls it an *incidental
  data structure*. You reach for a chocolate chip cookie and get raisin.
  Related: the steering wheel problem. Lending someone your car does not mean
  you both steer.

  A `shared_ptr` is as good as a global variable.

**Equality is about essence, not representation.** Two `vector`s with different
capacity are equal, because capacity is not salient to what a vector *is*.
Decide what your type's essence is, and let `==` say that. `x == y` iff `f(x) ==
f(y)` for every function you actually care about.

**Intrinsic vs extrinsic.** A circle's radius is intrinsic. Its x/y is a
relationship between the circle and a layout. Selection state is a relationship
with the UI. Push the extrinsic ones out to whoever owns the relationship, and
the leftover type becomes small, stable, and genuinely a value.

The naming corollary, and it does real work: **if you can't name it, you don't
know what it is; if you don't know what it is, you don't know what it isn't; and
then you don't know what code shouldn't be in it.** If moving x/y out feels
wrong, maybe the type was `CircularRegion` all along.

**Talk to the whole, not the part.** Prefer `vector<Shape>` over
`vector<Shape*>`, ask the layout about the circle rather than holding a circle
pointer, and keep relationships contained inside the type that owns them.

## If you use an ECS

An ECS already lands on the value side: components are data, systems are
functions over them. The two failure modes still arrive, wearing different
clothes.

- **Nexus** — a component that accumulated every field anyone needed, several of
  them meaningful only during one phase. Same disease as the fat class.
- **Graph of references** — a raw `Entity *` or a back-pointer held across
  frames. The fix is a generational handle resolved late, which is what a good
  ECS gives you. Use it; do not cache the resolved pointer.

Screen and UI state belongs on a singleton component rather than file-statics,
for the local-reasoning reason: one owner, findable, queryable from a test.

## Compile time is a real argument

Beyond design, free functions cut header coupling. A function on a class in a
header forces every translation unit that includes it to recompile when the
function changes; the same function in a `.cpp` does not. On a codebase where
you have already had to split a file to keep builds tolerable, this is not a
theoretical benefit.

## Do not overcorrect

- Objects are correct for things with real identity. Van Eerd's own projectors
  and cameras are objects, with a base class, and he says that is fine.
- It is a **gradient**, not a binary. Big values drift toward object-ness. A
  global `int` has identity and is therefore an object.
- Decide the leaning when you write the class: should this feel valuey or
  objecty? Will it have a copy constructor? An `==`?
- Do not shred a type into atoms. If pulling a field out leaves a
  meaningless husk, the field belonged, or the type needed a better name.
- **Performance: know which kind of codebase you are in.** Van Eerd's claim is
  that ~95% of code is not on a hot path, so write the clear version and measure
  before believing a copy is expensive. That holds for tools, services and
  application code, and it is right there.

  It does not transfer to a realtime codebase. In a game or anything with a
  frame budget, per-frame code is hot *by default* rather than by exception —
  the hot path is not a small annexe you visit occasionally, it is most of what
  runs. There, prefer the clear shape until it costs you, then measure and fix,
  but do not start from the assumption that cost is unlikely. Still measure
  before optimizing; just do not assume you are in the 95%.
