from ai.voice_form_pipeline import process_voice_form

result = process_voice_form(
    audio_path="Recording (3).wav",
    form_path="forms/seva_form.json"
)

print(result)
