#!/usr/bin/env python

import web
from web import form
import os
import json
import game
import sys
from settings import settings
import ast
import multiprocessing

urls = (
    '/', 'PageIndex',
    '/getnames', 'PageGetNames',
    '/python', 'Python',
    '/run/(.*?)/(.*?)/(\\d*)', 'PageRun'
)

app = web.application(urls, globals())

def debuggable_session(app):
    if web.config.get('_sess') is None:
        sess = web.session.Session(app, web.session.DiskStore('sessions'))
        web.config._sess = sess
        return sess
    return web.config._sess

sess = debuggable_session(app)

def hash(data):
    return hashlib.sha1(data).hexdigest()

def generate_salt(length=10):
    random.seed()
    pool = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join((random.choice(pool) for i in range(length)))

def template_closure(directory):
    templates = web.template.render(directory, globals={'sess': sess, 'settings': settings})

    def render(name, *params):
        return getattr(templates, name)(*params)

    return render

tpl = template_closure('t/')

class PageIndex:
    def GET(self):
        return tpl('layout')

class PageGetNames:
    def GET(self):
        files = os.listdir('robots')
        files = [x for x in files if os.path.isfile('robots/%s' % x)]
        files = [x for x in files if x.endswith('.py')]
        files = ['.'.join(x.split('.')[:-1]) for x in files]
        return json.dumps(files)

class Python:
    def GET(self):
        import sys
        return sys.version_info

def err(s):
    return json.dumps({'error': s})

def make_player(fname):
    with open(fname) as player_code:
        return game.Player(code=player_code.read())

map_data = ast.literal_eval(open('maps/default.py').read())

def run_match(fname1, fname2):
    class Logger:
        def __init__(self):
            self.output = ''

        def write(self, s):
            self.output += s

        def flush(self, s):
            pass

    sys.stdout = sys.stderr = Logger()

    game.init_settings(map_data)
    g = game.Game(make_player(fname1), make_player(fname2), record_turns=True)
    for i in xrange(settings.max_turns):
        print (' running turn %d ' % (g.turns + 1)).center(70, '-')
        g.run_turn()

    output = sys.stdout.output
    sys.stdout = sys.stderr = sys.__stdout__
    return {
        'output': output,
        'scores': g.get_scores(),
        'history': g.history
    }

def run_match_pool_worker(fname1, fname2, queue, count):
    result = run_match(fname1, fname2)
    queue.put(result['scores'])

class PageRun:
    def GET(self, name1, name2, count):
        web.header('Content-Type', 'application/json')

        name1 += '.py'
        name2 += '.py'
        for name in (name1, name2):
            if not os.path.isfile('robots/%s' % name):
                return err('%s is not a file' % name)

        if int(count) == 1:
            return json.dumps(run_match('robots/%s' % name1, 'robots/%s' % name2))

        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        queue = multiprocessing.Manager().Queue()

        params = ['robots/%s' % name1, 'robots/%s' % name2, queue]
        for i in xrange(int(count)):
            pool.apply_async(run_match_pool_worker, args=(params + [i]))

        pool.close()

        pool.join()


        def queue_get():
            try:
                return queue.get_nowait()
            except:
                return None

        all_scores = [x for x in iter(queue_get, None)]
        return json.dumps(all_scores)

if __name__ == '__main__':
    app.run()
