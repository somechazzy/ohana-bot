import re
import traceback
import greenlet
from actions import send_embed


# https://stackoverflow.com/a/46087477
class GreenAwait:
    def __init__(self, child):
        self.current = greenlet.getcurrent()
        self.value = None
        self.child = child

    def __call__(self, future):
        self.value = future
        self.current.switch()

    def __iter__(self):
        while self.value is not None:
            yield self.value
            self.value = None
            self.child.switch()


def gexec(code):
    child = greenlet.greenlet(exec)
    gawait = GreenAwait(child)
    child.switch(code, {'gawait': gawait})
    yield from gawait


async def aexec(code, message):
    green = greenlet.greenlet(gexec)
    code_lines = '\t'.join(code.splitlines(keepends=True))
    final_code = f'''
from actions import send_embed, send_message
from globals_.clients import discord_client
async def code_to_execute():
\tthis_channel = discord_client.get_channel({message.channel.id})
\toutputs={{}}
\t{code_lines}
\tfeedback = f"Code executed; no output given." if len(outputs) == 0 else "Code executed\\n\\n"
\tfor output in outputs:
\t    feedback += f"{{output}}: {{outputs[output]}}\\n"
\tawait send_embed(feedback.strip(), this_channel, emoji="🚀", color=0x000000, logging=False)
gawait(code_to_execute())
    '''
    gen = green.switch(final_code)
    for future in gen:
        await future


async def execute_owner_code_snippet(message):
    code_matches = re.findall("```python[\n]?[\\s\\S]+[\n]?```", message.content)
    if len(code_matches) == 0:
        code_matches = re.findall("```[\n]?[\\s\\S]+[\n]?```", message.content)
        if len(code_matches) == 0:
            return
        code = code_matches[0][3:len(code_matches[0])-3]
    else:
        code = code_matches[0][9:len(code_matches[0])-3]
    outputs = {}
    try:
        await aexec(code.strip(), message)
    except Exception as e:
        outputs["error"] = f"{e}\n{e.__cause__}\n\n{(traceback.format_exc())}"
        feedback = "Code executed\n\n"
        for output in outputs:
            feedback += f"{output}: {outputs[output]}\n"
        await send_embed(feedback.strip(), message.channel, emoji="🚀", color=0x000000, logging=False)
