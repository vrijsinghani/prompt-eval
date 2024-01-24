# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from .forms import HistoryForm
from .models import ModelResult
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.conf import settings
from collections import defaultdict
from helpers import *
from markdown import markdown
import requests
import logging
import openai

# Create your views here.
logger = logging.getLogger(__name__)  # <-- Add this line

def index(request):
    logger.debug('Got to index')
    # Page from the theme 
    return render(request, 'pages/index.html')

def evaluate(request):
    logger.debug('Got to evaluate')

    api_base_url=settings.API_BASE_URL

    client = openai.OpenAI(
    api_key="anything",
    base_url=api_base_url
    )

    models = get_models()
    if request.method == 'POST':
        questions = request.POST.get('questions').split('\n')
        prompt = request.POST.get('prompt')
        models_selected = request.POST.getlist('models')
        # Store values in the session
        request.session['questions'] = questions
        request.session['prompt'] = prompt
        request.session['models_selected'] = models_selected
        request.session.save()
        results = {}
        model_histories = {model: [{'role': 'system', 'content': prompt}] for model in models_selected}  # Initialize model histories

        for model in models_selected:
            logger.info("model: %s",model)
            for question in questions:
                logger.info("question: %s",question)
                model_histories[model].append({'role': 'user', 'content': question})  # Add the new question to the model's history
                response = client.chat.completions.create( 
                    model=model,
                    messages=model_histories[model],
                )
                answer = response.choices[0].message.content
                logger.info("answer: %s",answer)
                answer = answer.replace('\n', '<br>')  # Replace newlines with <br> tags
                model_histories[model].append({'role': 'assistant', 'content': answer})  # Add the model's response to its history
                if question not in results:
                    results[question] = {}
                results[question][model] = answer
                result = ModelResult(model_name=model, question=question, answer=answer)
                result.save()
                logger.debug("saved ModelResult")

        return render(request, 'pages/evaluate.html', {'results': results, 'models': models, 'questions': '\n'.join(questions),'prompt':prompt,'models_selected':models_selected, 'segment': 'evaluate' })
    else:
        logger.debug("got to else in evaluate.")
        # Retrieve values from the session
        questions = request.session.get('questions', ['What is 1+1'])
        prompt = request.session.get('prompt', 'You are an assistant.')
        models_selected = request.session.get('models_selected', ['ollama/openchat'])
        logger.debug(models_selected)
        return render(request, 'pages/evaluate.html', {'models': models, 'questions':'\n'.join(questions), 'prompt':prompt, 'models_selected':models_selected, 'segment': 'evaluate' })

def history(request):
    questions = ModelResult.objects.all().distinct()
    selected_question_ids = request.session.get('selected_question_ids', [])
    results = ModelResult.objects.all().order_by('timestamp')

    if request.method == 'POST':
        selected_question_ids = request.POST.getlist('question[]')
        request.session['selected_question_ids'] = selected_question_ids
        logger.debug(f"Selected question IDs: {selected_question_ids}")

        if 'delete' in request.POST:
            id_to_delete = request.POST.get('delete')
            ModelResult.objects.filter(id=id_to_delete).delete()
            messages.success(request, "Deleted successfully")
            return redirect('history')

        results = ModelResult.objects.filter(id__in=selected_question_ids).order_by('timestamp')
        logger.debug(f"Results: {results}")

    selected_questions = ModelResult.objects.filter(id__in=selected_question_ids)
    return render(request, 'pages/history.html', {'questions': questions, 'results': results, 'selected_questions': selected_questions})
