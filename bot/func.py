from google import genai
import logging
from config import settings


def format_exercise(exr_text: str): 
    print(settings.GEMINI_API_KEY)
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
    
    return response.text.strip()
