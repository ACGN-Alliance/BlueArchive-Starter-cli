import os

from utils.cmp import compare_images

if __name__ == '__main__':
    # 工作目录切换到项目根目录
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    print(compare_images('tests/1.png', 'tests/2.png'))
