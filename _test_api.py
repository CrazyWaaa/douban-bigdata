import sys, json
sys.path.insert(0, 'backend')
from app import app
client = app.test_client()

cases = [
    '/api/health',
    '/api/dashboard/summary',
    '/api/dashboard/summary_extended',
    '/api/movies/count_by_genre',
    '/api/movies/count_by_country',
    '/api/movies/count_by_year',
    '/api/movies/count_by_avg?dim=genre&limit=5',
    '/api/movies/count_by_avg?dim=country&limit=5',
    '/api/movies/count_by_avg?dim=year&limit=5',
    '/api/movies/count_by_director?limit=5',
    '/api/movies/count_by_language?limit=5',
    '/api/movies/count_by_decade',
    '/api/movies/rating_distribution',
    '/api/movies/runtime_distribution',
    '/api/movies/top_rated?limit=5',
    '/api/movies/paged?page=1&size=3&sort=rating&order=desc',
    '/api/movies/paged?page=1&size=3&sort=rating&order=asc',
    '/api/movies/paged?page=1&size=3&sort=year&order=desc',
    '/api/movies/paged?page=1&size=3&sort=rating_count&order=desc',
    '/api/movies/paged?page=1&size=3&genre=%E5%89%A7%E6%83%85',
    '/api/movies/paged?page=1&size=3&country=%E7%BE%8E%E5%9B%BD',
    '/api/movies/paged?page=1&size=3&year_from=2000&year_to=2010',
    '/api/movies/search?q=%E9%9C%B8%E7%8E%8B',
    '/api/movies/1292052',
    '/api/movies/1292052/related?limit=5',
    '/api/movies/1292052/neighbors',
]
ok = 0
fails = []
for url in cases:
    rv = client.get(url)
    short = url.split('?')[0].replace('/api/movies/','').replace('/api/','')[:32]
    if rv.status_code == 200:
        ok += 1
        print(f'  200  {short}')
    else:
        print(f'  {rv.status_code}  {short}')
        fails.append((url, rv.get_data(as_text=True)[:140]))

print(f'\\n{ok}/{len(cases)} pass')
for u, b in fails:
    print('FAIL', u, b)