from core.runtime.scheduler import JobScheduler

def ai_chat():
    print("AURa AI Interface — type \"exit\" to return")

    scheduler = JobScheduler()

    while True:
        msg = input("ai> ").strip()

        if msg == "exit":
            break

        job = scheduler.queue("docs", {"prompt": msg})
        print("AI job queued:", job)
