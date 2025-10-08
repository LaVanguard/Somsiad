from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string

def home(request):
    return render(request, 'home.html')

@require_http_methods(["POST"])
def query_api(request):
    """Mock API endpoint for chat queries - will be replaced with real LLM later"""
    question = request.POST.get('question', '')
    image = request.FILES.get('image', None)
    action = request.POST.get('action', None)

    # Handle image upload
    image_url = None
    if image:
        # For now, just create a data URL from the image
        # Later this will be saved to media folder
        import base64
        image_data = base64.b64encode(image.read()).decode('utf-8')
        image_url = f"data:{image.content_type};base64,{image_data}"

    # Generate mock response based on action
    if action == 'prokuratura':
        answer = '⚖️ ZGŁOSZENIE DO PROKURATURY REJONOWEJ\n\nSzanowny Panie Prokuratorze,\n\nNiniejszym zgłaszam sprawę wymagającą interwencji prokuratury. Sprawa dotyczy: "{}"\n\nZ poważaniem,\nZatroskany Obywatel\n\n(To jest mockowa odpowiedź dla śmiechu 😄)'.format(question)
    elif action == 'donos':
        answer = '📧 ANONIMOWY DONOS DO URZĘDU GMINY\n\nDo Wójta Gminy,\n\nUprzejmie informuję o nieprawidłowościach: "{}"\n\nProszę o dyskretną interwencję.\n\nPozdrawiam,\nAnonim z sąsiedztwa\n\n(To jest mockowa odpowiedź dla śmiechu 😄)'.format(question)
    elif action == 'straz':
        answer = '🚨 ZGŁOSZENIE DO STRAŻY MIEJSKIEJ\n\nWitam,\n\nProszę o pilną interwencję Straży Miejskiej w sprawie: "{}"\n\nZgłoszenie dotyczy naruszenia porządku publicznego.\n\nDziękuję,\nZaniepokojony Mieszkaniec\n\n(To jest mockowa odpowiedź dla śmiechu 😄)'.format(question)
    else:
        answer = 'Dziękuję za pytanie! Analizuję przepisy budowlane... (To jest mockowa odpowiedź. Wkrótce podłączymy prawdziwy LLM)'

    # Mock response
    context = {
        'question': question,
        'image_url': image_url,
        'answer': answer
    }

    html = render_to_string('partials/message.html', context)
    return HttpResponse(html)