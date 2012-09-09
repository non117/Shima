# -*- coding: utf-8 -*-
from shima import Icon

if __name__ == "__main__":
    command = u"face 7 base ffffff 778899 dot cheek 3 ★ 眼鏡 ほげ"
    icon = Icon()
    print icon.gen_icon(command)