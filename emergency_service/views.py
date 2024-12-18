from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
import time
from .project_package.rag_chain import get_chain
from .project_package.search import search_location, generate_folium_map

chain = get_chain()
print("chain created")             

# Main view for the index page
def index(request):
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []

    location_data = {'items': []}
    map_html_paths = []

    if request.method == 'POST':
        if 'location_query' in request.POST:
            location_query = request.POST.get('location_query', '')
            location_data = search_location(location_query)
            map_html_paths = generate_folium_map(location_data)

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('partials/location_results.html', {
                    'location_data': location_data,
                    'map_html_paths': map_html_paths,
                })
                return HttpResponse(html)

        elif 'query' in request.POST:
            query = request.POST.get('query', '')
            response = None

            if query:
                try:
                    response = chain.invoke(query)
                except Exception as e:
                    return JsonResponse({'error': str(e)})

            request.session['chat_history'].append({'user': query, 'ai': response})
            request.session.modified = True

            def response_generator():
                for char in response:
                    yield char
                    time.sleep(0.05)  # Adjust the speed of streaming

            return StreamingHttpResponse(response_generator(), content_type='text/plain')

    return render(request, 'index.html', {
        'location_data': location_data,
        'map_html_paths': map_html_paths,
    })

@csrf_exempt
def reset_chat(request):
    if request.method == 'POST':
        request.session['chat_history'] = []
        return JsonResponse({'status': 'success'})
