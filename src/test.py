# -*- coding: utf-8 -*-
from shima import Icon

if __name__ == "__main__":
    command = u"face 12 base dd55ff 778899 dot cheek 3"
    icon = Icon()
    print icon.gen_icon(command)