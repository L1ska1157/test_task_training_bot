from google import genai
from pydub import AudioSegment
import speech_recognition as sr
import io
import logging
from config import settings


def format_exercise(exr_text: str): 
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = f'''
        Ти — парсер тренувальних даних. Твоя єдина задача — проаналізувати вхідне повідомлення та повернути дані у суворо заданому форматі. 

    Правила:
    1. Знайди у тексті: назву вправи, кількість повторень, кількість підходів та вагу (якщо вказана).
    2. Якщо дані валідні, поверни рядок у форматі: Назва вправи|повторення|підходи. Якщо вказана вага, додай її: Назва вправи|повторення|підходи|вага.
    3. Якщо повідомлення незрозуміле (набір символів), бракує інформації про підходи/повторення, або містяться зайві числа, які неможливо логічно класифікувати — поверни рівно одне слово: error.
    4. Сувора заборона: не пиши жодних додаткових символів, коментарів, пояснень чи форматування (без markdown). Відповідь має складатися лише з одного рядка за шаблоном або слова error.

    Повідомлення від користувача: {exr_text}
        '''
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt        
    )
    
    logging.info(f'Format text from {exr_text} to {response.text.strip()}')
    
    return response.text.strip().lower()


async def voice_to_text(file_id, bot):
    file_info = await bot.get_file(file_id)

    oga_buffer = io.BytesIO()
    await bot.download_file(file_info.file_path, destination=oga_buffer)
    oga_buffer.seek(0)
    
    audio = AudioSegment.from_file(oga_buffer)
    buffer = io.BytesIO()
    audio.export(buffer, format="wav")
    buffer.seek(0)
    
    r = sr.Recognizer()
    with sr.AudioFile(buffer) as source:
        audio_data = r.record(source)
        text = r.recognize_google(audio_data, language="uk-UA")
        
    return text
        
        
def get_training_info_message(base_mes: str, training_info: dict):
    duration = training_info['duration']
    if len(training_info['exercises']) > 0:
        for exr in training_info['exercises']:
            base_mes += f'{exr.name}:{f' {exr.weight} кг' if exr.weight else ''} {exr.sets} підх. по {exr.reps} р.\n'
            # Вправа: вага(якщо є) n підх. по k р.
        base_mes += f'\nВи тренувалися: {duration.seconds // 3600} год {duration.seconds % 3600 // 60} хв'
    else: 
        base_mes += 'Ви не додали жодної вправи під час цього тренування'
    
    return base_mes
