import requests

#CUDA_VISIBLE_DEVICES="" HIP_VISIBLE_DEVICES="" ROCR_VISIBLE_DEVICES="" OLLAMA_LLM_LIBRARY=cpu ollama serve


url = "http://localhost:11434/api/generate"
SYSTEM_PROMPT = "Ты — русскоязычный помощник. Если вопрос связан со столбцами и данными:" \
"Если вопрос "

def script_run(prompt):
    payload = {
        'model': 'qwen2.5:3b',
        'prompt': SYSTEM_PROMPT + prompt,
        'stream': False
    }

    try:
        resp = requests.post(url, json=payload, timeout=(10, 300))
        resp.raise_for_status()
        data = resp.json()
        return data.get('response', '')

    except requests.HTTPError:
        return 'Окака Макака не может связаться с вашей моделью!'

    except TimeoutError:
        return 'Что-то не работает. . .'

    except Exception:
        return 'Караул, неизвестная ошибка! Окака акака в шоке.'