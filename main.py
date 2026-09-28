#!/usr/bin/env python3
"""
Kurumi Tokisaki AI - Main Entry Point
Supports both CLI and Web modes.
"""

import argparse
from character.manager import CharacterManager
from config import settings
from core.engine import CharacterEngine


def run_cli(reset_state: bool = False):
    """Run the CLI chat interface."""
    print("=" * 60)
    print("     KURUMI TOKISAKI AI - Spirit of Time")
    print("=" * 60)
    print()

    manager = CharacterManager()
    character = manager.load(settings.DEFAULT_CHARACTER)
    engine = CharacterEngine(character)

    if reset_state:
        engine.reset_everything()
        print("[Reset - starting with a blank slate: no memories, default mood/relationship]\n")
    
    print(f"Loaded: {character.identity['name']} - {character.identity.get('title', '')}")
    print(f"Model: {settings.MODEL}")
    print()
    print("Type 'exit', 'quit', or 'bye' to end the conversation.")
    print("Type '/stats' to see current state.")
    print("Type '/memory' to see long-term memories.")
    print("Type '/reset' to clear short-term memory.")
    print()
    print("-" * 60)
    print()
    
    # Initial greeting from Kurumi
    initial_response = engine.reply(
        "*A presence manifests from the shadows. The clock ticks.*"
    )
    if initial_response.success:
        print(f"Kurumi: {initial_response.text}")
        print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ("exit", "quit", "bye"):
                print()
                print("Kurumi: *The shadows recede. Her smile lingers.*")
                print('       "Ara ara~ Leaving so soon? The night is still young."')
                print('       *She fades into darkness, the glow of her clock eye the last to vanish.*')
                break
            
            elif user_input == "/stats":
                print_stats(engine)
                continue
            
            elif user_input == "/memory":
                print_memories(engine)
                continue
            
            elif user_input == "/reset":
                engine.memory.clear_conversation()
                print("[Short-term memory cleared.]")
                continue
            
            # Normal conversation
            response = engine.reply(user_input)
            
            if response.success:
                print(f"\nKurumi: {response.text}\n")
            else:
                print(f"\n[Error: {response.error}]\n")
                
        except KeyboardInterrupt:
            print("\n\nKurumi: *A sigh echoes through the shadows.*")
            print('       "Interrupted... How rude. But I shall wait."')
            break
        except EOFError:
            break
    
    print("\n[Conversation ended. The clock stops... for now.]")


def print_stats(engine):
    """Print current brain state statistics."""
    if hasattr(engine, 'brain') and hasattr(engine.brain, 'state'):
        state = engine.brain.state
        rel = state.relationship
        needs = state.needs
        
        print("\n" + "=" * 50)
        print("        KURUMI'S CURRENT STATE")
        print("=" * 50)
        print(f"Mood:          {state.mood}")
        print(f"Energy:        {state.energy}/100")
        print(f"Focus:         {state.focus}/100")
        print(f"Stress:        {state.stress}/100")
        print(f"Time Bullets:  {state.time_bullets_remaining}/12")
        print(f"Shadows:       {state.shadow_activity}")
        print(f"Zafkiel Eye:   {state.zafkiel_eye_state}")
        print(f"Timeline:      {state.current_timeline_stability:.0%}")
        print()
        print(f"Trust:         {rel.trust:.0f}/100")
        print(f"Familiarity:   {rel.familiarity:.0f}/100")
        print(f"Affection:     {rel.affection:.0f}/100")
        print(f"Respect:       {rel.respect:.0f}/100")
        print(f"Comfort:       {rel.comfort:.0f}/100")
        print()
        print(f"Social Need:   {needs.social:.0f}/100")
        print(f"Curiosity:     {needs.curiosity:.0f}/100")
        print(f"Time Pressure: {needs.time_pressure:.0f}/100")
        print(f"Secrecy:       {needs.secrecy:.0f}/100")
        print(f"Control:       {needs.control:.0f}/100")
        print()
        print(f"Goal:          {state.current_goal}")
        print(f"Action:        {state.current_action}")
        print("=" * 50 + "\n")


def print_memories(engine):
    """Print long-term memories."""
    memories = engine.brain.advanced_memory.long_term

    if not memories:
        print("\n[No long-term memories stored yet.]\n")
        return

    print(f"\n[Long-term Memories: {len(memories)} stored]")
    print("-" * 50)

    for i, mem in enumerate(memories[-10:], 1):  # Show last 10
        tag_str = f" [{', '.join(mem.tags)}]" if mem.tags else ""

        print(f"{i}. [{mem.memory_type}] (Imp: {mem.importance:.0%}){tag_str}")
        print(f"   {mem.content[:120]}{'...' if len(mem.content) > 120 else ''}")
        print()

    if len(memories) > 10:
        print(f"... and {len(memories) - 10} more memories.")
    print()


def main():
    parser = argparse.ArgumentParser(description="Kurumi Tokisaki AI Chatbot")
    parser.add_argument(
        "mode",
        nargs="?",
        default="cli",
        choices=["cli", "web", "desktop"],
        help="Run mode: cli (default), web, or desktop (floating window)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.WEB_PORT,
        help=f"Web server port (default: {settings.WEB_PORT})"
    )
    parser.add_argument(
        "--reset-state",
        action="store_true",
        help="Full reset before starting: mood/relationship/needs, long-term memory, and conversation history"
    )

    args = parser.parse_args()

    if args.mode == "web":
        import os
        import uvicorn
        if args.reset_state:
            os.environ["KURUMI_RESET_STATE"] = "1"
        from ui.app import app
        print(f"Starting Kurumi AI Web Server on port {args.port}...")
        print(f"Access at: http://localhost:{args.port}")
        uvicorn.run(app, host=settings.WEB_HOST, port=args.port)
    elif args.mode == "desktop":
        from desktop.app import main as desktop_main
        desktop_main(reset_state=args.reset_state)
    else:
        run_cli(reset_state=args.reset_state)


if __name__ == "__main__":
    main()