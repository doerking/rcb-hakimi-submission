import json, sys
sys.path.insert(0, '/mnt/i/hakimi-engineX/outputs/rcb/repo/.venv/lib/python3.14/site-packages')
sys.path.insert(0, '/mnt/i/hakimi-engineX/outputs/rcb/repo')
auth = json.load(open('/mnt/c/Users/Administrator/.pi/agent/auth.json'))
from structai import LLMAgent
a = LLMAgent(api_key=auth['openai']['key'], api_base='https://token.sensenova.cn/v1',
             model_version='sensenova-6.8-flash-lite', temperature=0, max_tokens=2500,
             time_limit=180, max_try=4)
for p in sys.argv[1:]:
    print("=" * 40, p)
    r = a("Describe this scientific figure in detail: axis labels, axis ranges (including tick values), curve colors/shapes, legend, key numeric annotations, title. Be precise about numerical values on the axes.",
          image_paths=[p], return_example={"d": "str"}, max_try=4)
    print(r)
