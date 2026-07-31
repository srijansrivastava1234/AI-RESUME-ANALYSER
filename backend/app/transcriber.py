import asyncio

# A realistic scam script timeline matching the keywords in the NLP Analyzer:
# Urgency: immediate, block, suspend, arrest, hurry
# Action: OTP, Anydesk, download, transfer, bank
# Authority: CBI, Police, Customs, Manager, FedEx
SCAM_SIMULATION_TIMELINE = [
    {"time": 2, "speaker": "Scammer", "text": "Hello? Am I speaking with the account holder?"},
    {"time": 4, "speaker": "User", "text": "Yes, who is this?"},
    {"time": 7, "speaker": "Scammer", "text": "This is Officer Sharma calling from FedEx Customs Support. We have detected a suspicious package in your name."},
    {"time": 12, "speaker": "User", "text": "Wait, FedEx? I haven't ordered anything! There must be a mistake."},
    {"time": 15, "speaker": "Scammer", "text": "Our records show illegal items. The CBI and local Police have initiated an immediate arrest warrant against you."},
    {"time": 21, "speaker": "User", "text": "CBI? Arrest? Please, how can we clarify this? I didn't do anything!"},
    {"time": 25, "speaker": "Scammer", "text": "To clear your name, you must download the Anydesk app right now and transfer a verification fee to our secure bank account immediately."},
    {"time": 32, "speaker": "User", "text": "Okay, okay, I am downloading it now. Please don't block my account."},
    {"time": 36, "speaker": "Scammer", "text": "Now open your bank app, input your PIN, and read me the OTP code that you receive to verify the transaction."}
]

async def stream_scam_simulation():
    """
    Asynchronously yields chunks of transcription and elapsed time,
    simulating a real-time call transcription.
    """
    accumulated_transcript = ""
    current_index = 0
    total_duration = 40  # 40 seconds total simulation time
    
    for sec in range(1, total_duration + 1):
        await asyncio.sleep(1)
        
        # Check if there is a transcript event at this second
        new_text = ""
        speaker = ""
        if current_index < len(SCAM_SIMULATION_TIMELINE) and SCAM_SIMULATION_TIMELINE[current_index]["time"] == sec:
            item = SCAM_SIMULATION_TIMELINE[current_index]
            speaker = item["speaker"]
            new_text = item["text"]
            current_index += 1
            
            if accumulated_transcript:
                accumulated_transcript += " "
            accumulated_transcript += f"[{speaker}]: {new_text}"
            
        yield {
            "elapsed_seconds": sec,
            "new_segment": {"speaker": speaker, "text": new_text} if new_text else None,
            "full_transcript": accumulated_transcript
        }
