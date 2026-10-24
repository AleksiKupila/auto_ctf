from src.services.ai_service import AgentSession
from argparse import ArgumentParser
from app.ui import build_ui


if __name__=="__main__":
    parser = ArgumentParser(
        prog="AutoCTF",
        description="An AI agent harness for cybersecurity-related tasks"
    )
    parser.add_argument('-u', '--ui', action='store_true', default=False, help="Use the graphical user interface")

    args = parser.parse_args()

    try:
        session = AgentSession()
        if args.ui:
            try:
                print(f"Launching UI...")
                demo = build_ui()
                demo.launch()
            except Exception as e:
                print(f"Failed to launch UI, aborting... {e}")
        else:
            goal = input("Enter instruction: ")
            agent = session.new_agent(goal)

            if agent:
                session.run_agent(agent)

    except Exception as e:
        print(f"Failed to create new session, aborting... {e}")

