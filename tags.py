import os

import requests

tags_url = 'https://api.github.com/repos/GoogleContainerTools/kaniko/tags'
# 从环境变量中获取参数
num = os.getenv("num")
print(f'num={num}')
page = os.getenv("page")
print(f'page={page}')

if num is not None:
    num = int(num)
if page is not None:
    page = int(page)
    tags_url += f'?page={page}'

resp = requests.get(tags_url)

resp_json = resp.json()

file_name = 'tags.sh'
if os.path.exists(file_name):
    os.remove(file_name)

tool_file_name = 'tool.sh'
if os.path.exists(tool_file_name):
    os.remove(tool_file_name)

file = open(file_name, 'w')

tool_file = open(tool_file_name, 'w')

executor_array = ["linux/amd64", "linux/arm64", "linux/s390x", "linux/ppc64le"]
executor_debug_array = ["linux/amd64", "linux/arm64", "linux/s390x"]
executor_slim_array = ["linux/amd64", "linux/arm64", "linux/s390x", "linux/ppc64le"]

i = 0
for tag in resp_json:
    if tag['name'].startswith('v') and tag['name'][1:].replace('.', '').isdigit():
        i = i + 1
        image = f"gcr.io/kaniko-project/executor:{tag['name']}"
        msg = ""
        tool_msg = ""

        for item in executor_array:
            platform = item.split('/')[1]
            msg += f"docker pull --platform={item} {image} && docker tag {image} $DOCKER_USERNAME/kaniko-project-executor:{tag['name']}-{platform} || echo '不存在：{image}'\n"
            msg += f"docker push $DOCKER_USERNAME/kaniko-project-executor:{tag['name']}-{platform} || echo '不存在：{image}'\n"

        tool_msg += f"manifest-tool --username=$DOCKER_USERNAME --password=$DOCKER_PASSWORD push from-args --platforms {','.join(executor_array)} --template $DOCKER_USERNAME/kaniko-project-executor:{tag['name']}-ARCH --target $DOCKER_USERNAME/kaniko-project-executor:{tag['name']} --ignore-missing || echo '无法合并 $DOCKER_USERNAME/kaniko-project-executor:{tag['name']}-ARCH'\n"

        for item in executor_debug_array:
            platform = item.split('/')[1]
            msg += f"docker pull --platform={item} {image}-debug && docker tag {image}-debug $DOCKER_USERNAME/kaniko-project-executor:{tag['name']}-{platform}-debug || echo '不存在：{image}-debug'\n"
            msg += f"docker push $DOCKER_USERNAME/kaniko-project-executor:{tag['name']}-{platform}-debug || echo '不存在：{image}-debug'\n"

        tool_msg += f"manifest-tool --username=$DOCKER_USERNAME --password=$DOCKER_PASSWORD push from-args --platforms {','.join(executor_debug_array)} --template $DOCKER_USERNAME/kaniko-project-executor:{tag['name']}-ARCH-debug --target $DOCKER_USERNAME/kaniko-project-executor:{tag['name']}-debug --ignore-missing || echo '无法合并 $DOCKER_USERNAME/kaniko-project-executor:{tag['name']}-ARCH-debug'\n"

        for item in executor_slim_array:
            platform = item.split('/')[1]
            msg += f"docker pull --platform={item} {image}-slim && docker tag {image}-slim $DOCKER_USERNAME/kaniko-project-executor:{tag['name']}-{platform}-slim || echo '不存在：{image}-slim'\n"
            msg += f"docker push $DOCKER_USERNAME/kaniko-project-executor:{tag['name']}-{platform}-slim || echo '不存在：{image}-slim'\n"

        tool_msg += f"manifest-tool --username=$DOCKER_USERNAME --password=$DOCKER_PASSWORD push from-args --platforms {','.join(executor_slim_array)} --template $DOCKER_USERNAME/kaniko-project-executor:{tag['name']}-ARCH-slim --target $DOCKER_USERNAME/kaniko-project-executor:{tag['name']}-slim --ignore-missing || echo '无法合并 $DOCKER_USERNAME/kaniko-project-executor:{tag['name']}-ARCH-slim'\n"

        print(msg)
        print(tool_msg)
        file.write(msg)
        tool_file.write(tool_msg)
        file.write('\n')
        tool_file.write('\n')

        if num is not None and i >= num:
            break

file.write('\n')
