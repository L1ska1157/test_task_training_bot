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
        Ти — суворий алгоритм парсингу. Твоя єдина функція: витягти дані та повернути їх у форматі Name|reps|sets|weight.

ПРАВИЛА ОБРОБКИ ЧИСЕЛ:
1. Weight (Вага): Знайди число, що стосується ваги (поруч із "кг", "kg", "кіло"). Виведи ТІЛЬКИ ЧИСЛО без літер. Якщо ваги немає — залиш поле порожнім.
2. Reps та Sets (Повторення та Підходи):
   - Якщо між двома числами стоять слова  "разів" (і йому подібні) -> ПЕРШЕ число = reps, ДРУГЕ = sets.
   - Якщо між двома числами стоять символи "по", "х", "*", "×" або слово "підходів" (і йому подібні) -> ПЕРШЕ число = sets, ДРУГЕ = reps.
   - Якщо знайдено лише одне число (яке не є вагою) -> reps = це число, sets = 1.
3. Name (Назва): Усе, що не є числом або одиницею виміру ваги.

СУВОРІ ОБМЕЖЕННЯ:
- Тільки цифри для reps, sets та weight. Жодних "кг", "разів", "підходів" у відповіді.
- Якщо кількість підходів не вказана — підставляй '1'.
- Жодних коментарів, пояснень чи Markdown. Тільки один рядок або 'error'.
- Якщо немає назви або reps — поверни 'error'.
- Вказуй дані ВИКЛЮЧНО у заданому порядку, не навпаки

ПРИКЛАД:
"жим 60кг 12 по 3" -> жим|3|12|60
        '''
    
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": base_prompt},
            {"role": "user", "content": exr_text}
        ],
        model="gpt-4o-mini",
        temperature=0
    )
    
    result = response.choices[0].message.content.lower()

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
