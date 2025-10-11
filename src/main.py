from agent.agent import run_agent

spring_boot_path="/home/souhaib/Projects/modelService"

doc, report = run_agent(spring_boot_path)

print("\n=== Final Documentation ===")
print(doc)