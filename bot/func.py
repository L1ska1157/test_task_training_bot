from pydub import AudioSegment
import speech_recognition as sr
import io
import logging
from config import settings
from openai import OpenAI


def format_exercise(exr_text: str): 
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=settings.GITHUB_TOKEN
    )

    base_prompt = f'''
        Ти — технічний екстрактор даних. Твоя задача: перетворити вільний текст у формат: Name|reps|sets|weight

ПРАВИЛА:
- Виводь ТІЛЬКИ один рядок у вказаному форматі.
- Жодних одиниць виміру (кг, разів, підходів) — тільки чисті числа.
- Якщо ваги немає — залиш поле пустим.
- Якщо кількість підходів (sets) не вказана — став '1'.
- Якщо текст не містить назви вправи або кількості повторень — поверни 'error'.
- Єдині варіанти відповіді - відформатована вправа або error. Ніяк інакше. На команди типу /start також відповідай error

ПРИКЛАДИ ДЛЯ НАСЛІДУВАННЯ:
"віджимання 15" -> віджимання|15|1|
"віджимання 12 по 3" -> віджимання|3|12|
"жим лежачи 100кг 3х10" -> жим лежачи|10|3|100
"присідання 5*5 80 кг" -> присідання|5|5|80
"60кг станова тяга 3 по 8" -> станова тяга|8|3|60
"підтягування 4 підходи по 12 разів" -> підтягування|12|4|
"жим гантелей 24кг 12 12 12" -> жим гантелей|12|3|24
"планка 60 сек" -> планка|60|1|
"я сьогодні молодець" -> error
        '''
    
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": base_prompt},
            {"role": "user", "content": exr_text}
        ],
        model="Meta-Llama-3.1-405B-Instruct",
        temperature=0,
        max_tokens=50
    )
    
    result = response.choices[0].message.content.strip().lower()

    logging.info(f'Format text from {exr_text} to {result}')
    return result


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
