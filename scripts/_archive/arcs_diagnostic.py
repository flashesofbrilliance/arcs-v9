#!/usr/bin/env python3
"""
ARCS INIT Diagnostic Tool
Interactive CLI for discovering your Atomic Family archetype
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple

# The Seven Archetypes
ARCHETYPES = {
    "Dreamer": {
        "acronym": "IPLR",
        "essence": "Curiosity, innovation, exploration",
        "question": "What if?",
        "description": "The child who takes things apart to see how they work"
    },
    "Guardian": {
        "acronym": "CEL",
        "essence": "Vigilance, urgency, protection",
        "question": "What's at stake?",
        "description": "The parent who watches for danger"
    },
    "Elder": {
        "acronym": "LRV",
        "essence": "Memory, wisdom, validation",
        "question": "Can we trust this?",
        "description": "The grandparent who remembers everything"
    },
    "Shapeshifter": {
        "acronym": "BFQ",
        "essence": "Flow, adaptation, resilience",
        "question": "What's possible now?",
        "description": "The river that finds new paths"
    },
    "Bridge": {
        "acronym": "CVI",
        "essence": "Connection, diversity, synthesis",
        "question": "What if we connected these?",
        "description": "The weaver who connects worlds"
    },
    "Heart": {
        "acronym": "SBW",
        "essence": "Communication, empathy, space-holding",
        "question": "What are you feeling?",
        "description": "The one who holds space for everyone"
    },
    "Sage": {
        "acronym": "FPER",
        "essence": "Discernment, precision, clarity",
        "question": "Is this signal or noise?",
        "description": "The jeweler who sees truth"
    }
}

class ARCSInitDiagnostic:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "somatic_scores": {},
            "mirror_scores": {},
            "pattern_scores": {},
            "consensus": {}
        }

    def clear_screen(self):
        """Clear terminal screen"""
        import os
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_header(self, text: str):
        """Print formatted header"""
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60 + "\n")

    def print_archetype(self, name: str):
        """Print archetype info beautifully"""
        info = ARCHETYPES[name]
        print(f"\n🔹 {name.upper()} ({info['acronym']})")
        print(f"   {info['description']}")
        print(f"   Essence: {info['essence']}")
        print(f"   Question: \"{info['question']}\"")

    def welcome(self):
        """Welcome screen"""
        self.clear_screen()
        print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║            THE BOOK OF ARCS - INIT DIAGNOSTIC            ║
║                                                          ║
║            Discover Your Atomic Family Archetype         ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

Welcome! This diagnostic will help you discover your:
  • PRIMARY archetype (what energizes you)
  • SHADOW archetype (what you've exiled)
  • SECONDARY archetype (how you cope)

We'll use three methods:
  1. Somatic Scan (body-based)
  2. Mirror Test (relational)
  3. Pattern Analysis (receipt-based)

This will take about 10-15 minutes.
Take your time. Trust your gut, not your head.

        """)
        input("Press ENTER when ready to begin...")

    def somatic_scan(self):
        """Body-based diagnostic"""
        self.clear_screen()
        self.print_header("PART 1: SOMATIC SCAN - Body Knows First")

        print("""
I'll describe seven energies. For each one, notice your BODY's reaction.
Don't think—just FEEL.

Rate each energy:
  +2 = Body OPENED (leaned in, relaxed, excited)
  +1 = Slightly drawn to it
   0 = Neutral
  -1 = Slightly pulled back
  -2 = Body CONTRACTED (tensed, resisted, pulled away)

Close your eyes after reading each description.
Take 10 seconds to feel your body's response.
        """)
        input("\nPress ENTER to continue...")

        scenarios = {
            "Dreamer": """
You're in a garage at midnight. Before you: scattered parts, half-built 
machines, sketches everywhere. No one's watching. You're taking something 
apart just to see how it works. Time disappears. Your hands move before 
you think.
            """,
            "Guardian": """
There's a deadline—24 HOURS. Everyone else is panicking. But you feel...
ALIVE. Focused. Clear. The pressure doesn't drain you—it SHARPENS you. 
You know exactly what to do.
            """,
            "Elder": """
Someone tells you a story that doesn't add up. You remember: they said 
something different last time. You don't call them out—you just hold 
the truth quietly. You've been tracking patterns for YEARS.
            """,
            "Shapeshifter": """
The plan falls apart. Everyone freezes. You... PIVOT. Instantly. 
"Okay, new plan." You're not attached to how things "should" be—
you're interested in what's possible NOW.
            """,
            "Bridge": """
You're in a room where no one speaks the same language. But you see 
connections. You introduce the scientist to the artist. The conservative 
to the radical. You weave worlds together.
            """,
            "Heart": """
Two people are fighting. Neither is hearing the other. You step in: 
"What I hear you saying is..." You translate. You hold space. You make 
sure everyone feels HEARD.
            """,
            "Sage": """
Someone presents ten ideas. Nine are noise. One is brilliant. You see 
it immediately. "This one. The rest are distractions." You're not 
mean—you're just PRECISE.
            """
        }

        scores = {}
        for archetype, scenario in scenarios.items():
            print(f"\n{'='*60}")
            self.print_archetype(archetype)
            print(scenario)
            print("\nClose your eyes. Take 10 seconds. Feel your body.")

            while True:
                try:
                    response = input("\nYour body's reaction (-2 to +2): ").strip()
                    score = int(response)
                    if -2 <= score <= 2:
                        scores[archetype] = score
                        break
                    else:
                        print("Please enter a number from -2 to +2")
                except ValueError:
                    print("Please enter a valid number")

        self.results["somatic_scores"] = scores

        # Show summary
        print("\n" + "="*60)
        print("SOMATIC SCAN COMPLETE")
        print("="*60)

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        print("\nYour body's responses (strongest to weakest):")
        for arch, score in sorted_scores:
            emoji = "✅" if score > 0 else "❌" if score < 0 else "➖"
            print(f"  {emoji} {arch:15} {score:+2}")

        input("\nPress ENTER to continue to Mirror Test...")

    def mirror_test(self):
        """Relational diagnostic"""
        self.clear_screen()
        self.print_header("PART 2: MIRROR TEST - Who Reflects You?")

        print("""
Think of the 3 PEOPLE YOU FEEL MOST ALIVE WITH.
Not who you admire from afar—people where you think: 
"We're the same species."

For each person, select which energies they express MOST.
(You can select multiple per person)
        """)

        all_selections = {arch: 0 for arch in ARCHETYPES.keys()}

        for person_num in range(1, 4):
            print(f"\n{'='*60}")
            print(f"PERSON #{person_num}")
            print("="*60)
            name = input("Their name (or initials): ").strip()

            print(f"\nWhat energy does {name} express? (Enter numbers, comma-separated)")
            for i, (arch, info) in enumerate(ARCHETYPES.items(), 1):
                print(f"  {i}. {arch:15} - {info['essence']}")

            while True:
                try:
                    selections = input("\nYour choices (e.g., 1,3,5): ").strip()
                    selected_nums = [int(x.strip()) for x in selections.split(",")]
                    if all(1 <= n <= 7 for n in selected_nums):
                        arch_list = list(ARCHETYPES.keys())
                        for num in selected_nums:
                            selected_arch = arch_list[num - 1]
                            all_selections[selected_arch] += 1
                        break
                    else:
                        print("Please enter numbers between 1 and 7")
                except (ValueError, IndexError):
                    print("Please enter valid numbers separated by commas")

        self.results["mirror_scores"] = all_selections

        # Show summary
        print("\n" + "="*60)
        print("MIRROR TEST COMPLETE")
        print("="*60)

        sorted_selections = sorted(all_selections.items(), key=lambda x: x[1], reverse=True)
        print("\nThe energies your people express most:")
        for arch, count in sorted_selections:
            if count > 0:
                print(f"  {'⭐' * count} {arch:15} ({count} people)")

        print("""
\nINSIGHT:
The energy your people share is likely YOUR primary (you're drawn to 
your reflection) OR your shadow (you crave what you've exiled).
        """)

        input("Press ENTER to continue to Pattern Analysis...")

    def pattern_analysis(self):
        """Receipt-based diagnostic"""
        self.clear_screen()
        self.print_header("PART 3: PATTERN ANALYSIS - What Makes You Stay/Leave?")

        print("""
Think of your last 3-5 MAJOR DECISIONS (jobs, relationships, projects).

For each, I'll ask:
  • What made you STAY (or what would have made you stay)?
  • What made you LEAVE (or what made you dissatisfied)?

We'll identify your patterns.
        """)
        input("Press ENTER to begin...")

        stay_reasons = {
            "Dreamer": ["challenged to grow", "new learning", "exploration", "novelty", "creative freedom"],
            "Guardian": ["clear mission", "urgency", "stakes", "protecting something"],
            "Elder": ["trust built", "promises kept", "validated", "respect earned"],
            "Shapeshifter": ["could adapt", "flexibility", "room to pivot", "not rigid"],
            "Bridge": ["diversity valued", "connections", "cross-pollination"],
            "Heart": ["deep communication", "felt heard", "emotional safety"],
            "Sage": ["high standards", "excellence", "quality mattered", "no compromise"]
        }

        leave_reasons = {
            "Dreamer": ["became routine", "no growth", "rigid", "boring"],
            "Guardian": ["no urgency", "complacent", "stakes too low"],
            "Elder": ["promises broken", "trust violated", "disrespected"],
            "Shapeshifter": ["too rigid", "couldn't adapt", "stuck"],
            "Bridge": ["homogeneous", "narrow", "isolated"],
            "Heart": ["not heard", "emotionally unsafe", "used"],
            "Sage": ["mediocrity", "low standards", "sloppy work"]
        }

        pattern_scores = {arch: 0 for arch in ARCHETYPES.keys()}

        num_decisions = int(input("\nHow many decisions to analyze (3-5)? "))

        for i in range(1, num_decisions + 1):
            print(f"\n{'='*60}")
            print(f"DECISION #{i}")
            print("="*60)
            decision = input("What was it (job, relationship, project)? ").strip()

            print(f"\nWhat made you STAY (or would have made you stay) in {decision}?")
            print("(Free text - describe in a few words)")
            stay_answer = input("> ").strip().lower()

            print(f"\nWhat made you LEAVE (or made you dissatisfied) in {decision}?")
            print("(Free text - describe in a few words)")
            leave_answer = input("> ").strip().lower()

            # Simple keyword matching
            for arch, keywords in stay_reasons.items():
                if any(keyword in stay_answer for keyword in keywords):
                    pattern_scores[arch] += 2

            for arch, keywords in leave_reasons.items():
                if any(keyword in leave_answer for keyword in keywords):
                    pattern_scores[arch] += 1

        self.results["pattern_scores"] = pattern_scores

        # Show summary
        print("\n" + "="*60)
        print("PATTERN ANALYSIS COMPLETE")
        print("="*60)

        sorted_patterns = sorted(pattern_scores.items(), key=lambda x: x[1], reverse=True)
        print("\nYour decision patterns (strongest to weakest):")
        for arch, score in sorted_patterns:
            if score > 0:
                print(f"  📊 {arch:15} {score} matches")

        input("\nPress ENTER to see your final results...")

    def calculate_consensus(self):
        """Calculate final archetype based on all three methods"""
        # Weight the scores
        final_scores = {arch: 0 for arch in ARCHETYPES.keys()}

        # Somatic (weight: 3x - body doesn't lie)
        for arch, score in self.results["somatic_scores"].items():
            final_scores[arch] += score * 3

        # Mirror (weight: 2x)
        for arch, count in self.results["mirror_scores"].items():
            final_scores[arch] += count * 2

        # Pattern (weight: 2x)
        for arch, score in self.results["pattern_scores"].items():
            final_scores[arch] += score * 2

        sorted_final = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)

        self.results["consensus"] = {
            "primary": sorted_final[0][0],
            "secondary": sorted_final[1][0],
            "shadow": sorted_final[-1][0],  # Lowest score = likely shadow
            "all_scores": dict(sorted_final)
        }

        return sorted_final

    def display_results(self, sorted_scores):
        """Display final comprehensive results"""
        self.clear_screen()

        print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║               YOUR ATOMIC SIGNATURE                      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
        """)

        primary = self.results["consensus"]["primary"]
        secondary = self.results["consensus"]["secondary"]
        shadow = self.results["consensus"]["shadow"]

        print("\n" + "="*60)
        print("PRIMARY ARCHETYPE")
        print("="*60)
        self.print_archetype(primary)
        print("\n✨ This is your ZONE OF GENIUS—what energizes you most.")

        print("\n" + "="*60)
        print("SECONDARY ARCHETYPE")
        print("="*60)
        self.print_archetype(secondary)
        print("\n🤝 This is how you COPE—your bridge between primary and shadow.")

        print("\n" + "="*60)
        print("SHADOW ARCHETYPE (Potential)")
        print("="*60)
        self.print_archetype(shadow)
        print("\n🌑 This might be what you've EXILED—your growth edge.")
        print("   (Note: Shadow scoring is tentative—requires deeper work)")

        print("\n" + "="*60)
        print("COMPLETE PROFILE")
        print("="*60)
        print("\nYour integrated scores across all three methods:")
        for arch, score in sorted_scores:
            bar = "█" * max(0, int(score / 2))
            print(f"  {arch:15} {bar} ({score})")

        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print(f"""
1. READ: Your primary archetype's Genesis parable
   → Parable on {primary} (Book I)

2. EXPLORE: Your shadow archetype's Genesis parable  
   → Parable on {shadow} (Book I)

3. BOND: Read the relationship between your primary and shadow
   → The {primary} + {shadow} bond (Book II)

4. DEEPEN: Try Foundational Shift #1 (Shadow Integration)
   → 3-6 months of integration work

5. TRACK: Start keeping decision receipts
   → See Appendix B for templates
        """)

        return primary, secondary, shadow

    def save_results(self):
        """Save results to JSON file"""
        filename = f"arcs_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 Results saved to: {filename}")
        print("   You can review this anytime!")

    def run(self):
        """Main execution flow"""
        self.welcome()
        self.somatic_scan()
        self.mirror_test()
        self.pattern_analysis()
        sorted_scores = self.calculate_consensus()
        self.display_results(sorted_scores)

        save = input("\nWould you like to save these results? (y/n): ").strip().lower()
        if save == 'y':
            self.save_results()

        print("\n" + "="*60)
        print("Thank you for taking the ARCS INIT Diagnostic!")
        print("May you see yourself clearly and love yourself fully.")
        print("="*60 + "\n")

if __name__ == "__main__":
    diagnostic = ARCSInitDiagnostic()
    diagnostic.run()
