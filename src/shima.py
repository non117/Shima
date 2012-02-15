# coding:utf-8
import Image, ImageChops
import re
from os import path
from random import randint

from lib.core import Output
from lib.twitter.api import Api

class shima(Output):
    ''' settings.py
    "shima":{"include":["twitter"], "screen_name":"YOUR USERNAME"}
    '''
    def init(self):
        if isinstance(self.twitter, dict):
            self.twitter = [self.twitter]
        apilist = [Api(twi["atoken"],twi["atokensecret"]) for twi in self.twitter]
        self.api = None
        for a in apilist:
            user = a.user_timeline(count=1)[0]["user"]
            name = user["screen_name"]
            if name == self.screen_name:
                self.api = a
        self.icon = Icon()
        self.icon_path = self.icon.base_path + "/icon.png"
    
    def throw(self, packet):
        text = packet["data"]
        if self.icon.gen_icon(text):
            self.api.upload_icon(self.icon_path)

class Icon(object):
    def __init__(self):
        regexp_str = u"(?P<face>(face|顔|かお|表情)\s?((1[0-2])|[1-9]{1}))|"\
                    + u"(?P<ribbon>(ribbon|リボン))|"\
                    + u"(?P<cheek>(cheek|ほほ|頬)\s?[123])|"\
                    + u"(?P<pants>(dot|stripe|(しま|縞)(ぱん|パン)|(水|みず)(たま|玉)))|"\
                    + u"(?P<color>(\d{1,3}\s?,\s?\d{1,3}\s?,\s?\d{1,3})|[0-9a-fA-F]{6})|"\
                    + u"(?P<base_color>(base|ベース)\s?((\d{1,3}\s?,\s?\d{1,3}\s?,\s?\d{1,3})|[0-9a-fA-F]{6}))|"\
                    + u"(?P<nopants>(nopants|のーぱん|ノーパン|(ぱんつ)?すぽーん|キャストオフ|cast\s?off))"
        self.regexp = re.compile(regexp_str)
        self.stripe_regexp = re.compile(u"stripe|(しま|縞)(ぱん|パン)")
        self.dot_regexp = re.compile(u"dot|(水|みず)(たま|玉)")
        
        self.base_path = path.join(path.dirname(path.abspath(__file__)),"icon")
        base = Image.open(self.base_path + "/non_nopants.png")
        base_pants = Image.open(self.base_path + "/non_pants.png")
        cheek1 = Image.open(self.base_path + "/cheek1.png")
        cheek2 = Image.open(self.base_path + "/cheek2.png")
        cheek3 = Image.open(self.base_path + "/cheek3.png")
        face1 = Image.open(self.base_path + "/face1.png")
        face2 = Image.open(self.base_path + "/face2.png")
        face3 = Image.open(self.base_path + "/face3.png")
        face4 = Image.open(self.base_path + "/face4.png")
        face5 = Image.open(self.base_path + "/face5.png")
        face6 = Image.open(self.base_path + "/face6.png")
        face7 = Image.open(self.base_path + "/face7.png")
        face8 = Image.open(self.base_path + "/face8.png")
        face9 = Image.open(self.base_path + "/face9.png")
        face10 = Image.open(self.base_path + "/face10.png")
        face11 = Image.open(self.base_path + "/face11.png")
        face12 = Image.open(self.base_path + "/face12.png")
        frame = Image.open(self.base_path + "/frame.png")
        ribbon = Image.open(self.base_path + "/ribbon.png")
        dot = Image.open(self.base_path + "/spotted_mask.png")
        stripe = Image.open(self.base_path + "/stripe_mask.png")
        base_mask = Image.open(self.base_path + "/pants_base_mask.png")
        self.image = {"normal":base, "pants":base_pants, "cheek":{1:cheek1, 2:cheek2, 3:cheek3},
                      "face":{1:face1, 2:face2, 3:face3, 4:face4, 5:face5, 
                              6:face6, 7:face7, 8:face8, 9:face9, 10:face10, 11:face11, 12:face12},
                       "frame":frame,
                      "ribbon":ribbon, "dot":dot, "stripe":stripe, "base_mask":base_mask}
        
        self.base_image = self.image["pants"]
        self.pattern_image = self.image["stripe"]
        self.color_image = Image.new("RGBA", (240, 240), 0x000000)
        self.base_color_image = Image.new("RGBA", (240, 240), 0xffffff)
        self.cheek_image = self.image["cheek"][1]
        self.face_image = self.image["face"][1]
        self.equip_pants = True
        

    def command_perser(self, text):
        ''' userstreamから受け取った文字列からコマンドを取り出し辞書で返す '''
        itr = self.regexp.finditer(text)
        command = {}
        for i in itr:
            for c in ("face", "ribbon", "cheek", "pants", "nopants", "color", "base_color"):
                dic = i.groupdict()
                if dic[c]:
                    command.update({c:dic[c]})
        if not command:
            return None
        self.command = self._validate(command)
        return self.command

    def _validate(self, command):
        ''' commandの辞書の値が正しいかチェックする '''
        if command.has_key("face"):
            num = int(re.compile("\d{1,2}").search(command["face"]).group())
            if num > 0 and num < 13:
                command["face"] = num
            else:
                del command["face"]
        if command.has_key("cheek"):
            num = int(re.compile("\d").search(command["cheek"]).group())
            if num == 1 or num == 2 or num == 3:
                command["cheek"] = num
            else:
                del command["cheek"]
        if command.has_key("pants"):
            if self.stripe_regexp.search(command["pants"]):
                command["pants"] = "stripe"
            elif self.dot_regexp.search(command["pants"]):
                command["pants"] = "dot"
            else:
                del command["pants"]
        if command.has_key("color"):
            color_str = command["color"]
            if ',' in color_str: # ','区切りの色指定の場合.
                color = tuple(map(int, color_str.split(',')))
            else: # 16進カラーコードの場合.
                color = (int(color_str[:2],16), int(color_str[2:4],16), int(color_str[4:6],16))
            if self._color_is_valid(color): # RGB範囲チェック
                command["color"] = color
            else:
                del command["color"]
        if command.has_key("base_color"):
            base_color_10 = re.compile("\d{1,3}\s?,\s?\d{1,3}\s?,\s?\d{1,3}").search(command["base_color"])
            base_color_16 = re.compile("[0-9a-fA-F]{6}").search(command["base_color"])
            if base_color_10:
                base_color_10 = base_color_10.group()
                base_color = tuple(map(int, base_color_10.split(',')))
            elif base_color_16:
                base_color_16 = base_color_16.group()
                base_color = (int(base_color_16[:2],16), int(base_color_16[2:4],16), int(base_color_16[4:6],16))
            if self._color_is_valid(base_color): # RGB範囲チェック
                command["base_color"] = base_color
            else:
                del command["base_color"]
        if command.has_key("nopants") and command.has_key("pants"):
            del command["nopants"]
        return command

    def _color_is_valid(self, color):
        for c in color:
            if c >= 0 and c < 256:
                return True

    def gen_icon(self, text):
        if not self.command_perser(text):
            return False
        self.icon = Image.new("RGBA", (240, 240), 0x00ffff)
        if self.command.has_key("pants") or self.command.has_key("color") or self.command.has_key("base_color"):
            self._gen_pants()
            self.equip_pants = True
        elif self.command.has_key("nopants"):
            self._gen_nopants()
            self.equip_pants = False
        elif not self.equip_pants:
            self._gen_nopants()
        else:
            self._gen_pants()
        self._gen_face()
        self.icon.save(self.base_path + "/icon.png")
        return self.icon

    def _gen_pants(self):
        if self.command.has_key("pants"):
            self.base_image = self.image["pants"]
            self.pattern_image = self.image[self.command["pants"]]
        if self.command.has_key("color"):
            self.color_image = Image.new("RGBA", (240, 240), self.command["color"])
        if self.command.has_key("base_color"):
            self.base_color_image = Image.new("RGBA", (240, 240), self.command["base_color"])
        
        self.icon.paste(self.base_image, mask=self.base_image)
        self.icon = ImageChops.composite(self.icon, self.base_color_image, self.image["base_mask"])
        self.icon = ImageChops.composite(self.icon, self.color_image, self.pattern_image)
        if self.command.has_key("ribbon"):
            self.icon.paste(self.image["ribbon"], mask=self.image["ribbon"])
        self.icon.paste(self.image["frame"], mask=self.image["frame"])

    def _gen_nopants(self):
        self.base_image = self.image["normal"]
        self.icon.paste(self.base_image, mask=self.base_image)

    def _gen_face(self):
        if self.command.has_key("cheek"):
            self.cheek_image = self.image["cheek"][self.command["cheek"]]
        if self.command.has_key("face"):
            self.face_image = self.image["face"][self.command["face"]]
        self.icon.paste(self.face_image, mask=self.face_image)
        self.icon.paste(self.cheek_image, mask=self.cheek_image)

def random_color():
    color = (randint(0,255), randint(0,255), randint(0,255))
    return color
