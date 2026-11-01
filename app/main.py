import os
import uuid
from typing import Dict, Any
from dotenv import load_dotenv

from app.graph_workflow import app_graph, AgentState
from app.memory_manager import MemoryManager

load_dotenv()

class AISoftwareCompany:
    def __init__(self):
        print("🚀 Initializing AI Software Company Foundation...")
        self.memory = MemoryManager()
        self.workflow = app_graph

    def run_project(self, task_goal: str):
        """
        Executes the full lifecycle of a software project.
        """
        # 1. Initialize Session
        session_id = str(uuid.uuid4())
        print(f"📁 Starting project session: {session_id}")

        # 2. Consult Long-Term Memory (RAG)
        # Before the graph starts, we check if the company has lessons for this task
        print("🧠 Consulting Company Playbook for historical lessons...")
        past_lessons = self.memory.query_lessons(task_goal)
        
        lesson_context = "No previous lessons found."
        if past_lessons:
            lesson_context = "\n".join([f"- {l}" for l in past_lessons])
            print(f"💡 Found {len(past_lessons)} relevant lessons to guide the agents.")

        # 3. Prepare Initial State
        initial_state: AgentState = {
            "task": f"{task_goal}\n\nHistorical Lessons: {lesson_context}",
            "research": "",
            "architecture": "",
            "code": "",
            "qa_feedback": "",
            "status": "planning",
            "iterations": 0,
            "history": [f"Project started: {task_goal}"]
        }

        # 4. Execute the Graph Workflow
        print("⚙️  Executing multi-agent workflow...")
        try:
            # we stream the output to see the agents working in real-time
            final_state = None
            for output in self.workflow.stream(initial_state):
                for node_name, state_update in output.items():
                    print(f"  [Node: {node_name}] -> {state_update.get('history', [''])[-1]}")
                    # Persist state to Redis for session recovery
                    self.memory.save_session(session_id, state_update)
                    # Log event to Redis history
                    self.memory.add_to_history(session_id, f"Node {node_name} executed")
                final_state = output # Capture the last emitted state

            # 5. Post-Project Distillation (PostMortem)
            if final_state:
                self._perform_post_mortem(session_id, final_state)

            print("\n✅ Project Lifecycle Complete.")
            return final_state

        except Exception as e:
            print(f"❌ Critical System Failure: {e}")
            return None

    def _perform_post_mortem(self, session_id: str, final_state: Dict[str, Any]):
        """
        Analyzes the run and saves a distilled lesson to ChromaDB.
        """
        print("📝 Performing PostMortem analysis...")
        
        # We extract the final state values to build the lesson
        task = final_state.get("task", "Unknown Task")
        feedback = final_state.get("qa_feedback", "No feedback")
        iterations = final_state.get("iterations", 0)
        
        # In a full implementation, the PostMortem agent (from agents.py) 
        # would process this via an LLM. Here we simulate the distillation:
        if iterations > 1:
            lesson = f"Task '{task}' required {iterations} iterations. Key friction point: {feedback[:100]}..."
            self.memory.store_lesson(
                lesson=lesson,
                task_context=task,
                metadata={"iterations": iterations, "session_id": session_id}
            )
            print("💾 Lesson stored in Company Playbook.")

if __name__ == "__main__":
    company = AISoftwareCompany()
    
    # Example Task: Build a simple secure password validator
    goal = "Create a Python script that validates passwords for 12+ chars, 1 digit, and 1 special char. It must be production-ready."
    company.run_project(goal)
