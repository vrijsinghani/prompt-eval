from celery import shared_task

@shared_task
def add(x, y):
    return x + y

from celery import shared_task
from .models import ModelResult
import openai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def evaluate_task(self, questions, prompt, models_selected):
    api_base_url=settings.API_BASE_URL
    client = openai.OpenAI(
        api_key="anything",
        base_url=api_base_url
    )
    results = {question: {model: None for model in models_selected} for question in questions}
    model_histories = {model: [{'role': 'system', 'content': prompt}] for model in models_selected}  # Initialize model histories
    total = len(models_selected) * len(questions)
    self.update_state(state='PROGRESS', meta={'current': 0, 'total': total})
    for i, model in enumerate(models_selected):
        self.update_state(state='PROGRESS', meta={'current': i*len(questions), 'total': total, 'current_model': model})
        for j, question in enumerate(questions):
            model_histories[model].append({'role': 'user', 'content': question})  # Add the new question to the model's history
            response = client.chat.completions.create(
                model=model,
                messages=model_histories[model],
            )
            answer = response.choices[0].message.content
            answer = answer.replace('\n', '<br>')  # Replace newlines with <br> tags
            model_histories[model].append({'role': 'assistant', 'content': answer})  # Add the model's response to its history
            result = ModelResult(model_name=model, question=question, answer=answer)
            result.save()
            results[question][model] = answer
            logger.debug(f'Stored answer: {answer}')
            self.update_state(state='PROGRESS', meta={'current': i*len(questions)+j+1, 'total': total, 'current_model': model})
    logger.debug(f"Results: {results}")
    return results
