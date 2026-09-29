import sys

if sys.platform == "win32":
    import subprocess

    _original_popen = subprocess.Popen


    class _Utf8Popen(_original_popen):
        def __init__(self, *args, **kwargs):
            if kwargs.get("text") or kwargs.get("universal_newlines"):
                kwargs.setdefault("encoding", "utf-8")
                kwargs.setdefault("errors", "replace")
            super().__init__(*args, **kwargs)


    subprocess.Popen = _Utf8Popen

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from OmniAgent import OmniAgent

if __name__ == '__main__':
    agent = OmniAgent()
    while True:
        print(end='\n')
        # (1=查看所有mcp列表，2=连接mcp，3=列举mcp工具，其他都是与agent对话)
        msg = str(input('用户：'))
        if msg == 'quit':
            print('bye!')
            break
        if msg == '1':
            print(agent.get_mcp_list())
            continue
        elif msg == '2':
            server_name = input('server_name:')
            url = input('url:')
            print(agent.connect_mcp(server_name, url))
            continue
        elif msg == '3':
            print(agent.get_mcp_tools())
            continue
        print('AI:', agent.chat(msg, user_id='张三'))
