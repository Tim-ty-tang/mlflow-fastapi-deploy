import subprocess
import logging
import os

logging.basicConfig(level=logging.INFO, format='{asctime} {levelname:8s} {message}', style='{')
logger = logging.getLogger('root')

output1 = subprocess.Popen(['git', 'describe', '--tags'], stdout=subprocess.PIPE)
output2 = subprocess.Popen(["sed", "s:^rel/::"], stdin=output1.stdout, stdout=subprocess.PIPE)
output1.wait()
git_tag = output2.communicate()[0]

logger.info(git_tag)
txt = git_tag.decode("utf-8").strip()
txts = txt.split('-')
logger.info(txts)
os.environ["MODEL_NAME"] = txts[0]
os.environ["VER"] = "-".join(txts[0:2])
if len(txts) >= 3:
    os.environ["CONF_NAME"] = txts[2]
if len(txts) >= 4:
    os.environ["CONF_LOCAL_PATH"] = txts[3]

logger.info(f'{os.environ["MODEL_NAME"]}, {os.environ["VER"]}')
if len(txts) >= 4:
    logger.info(f'{os.environ["CONF_NAME"]}, {os.environ["CONF_LOCAL_PATH"]}')