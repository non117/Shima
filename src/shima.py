# coding:utf-8
import Image, ImageChops
import re
from os import path
from random import randint, random

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
        self.regexp_dic = {
                        ur"face \2,,,":ur"(face|顔|かお|表情)\s?((1[0-2])|[1-9]{1})",
                        ur"ribbon,,,":ur"(ribbon|リボン)",
                        ur"cheek \2,,,":ur"(cheek|ほほ|頬)\s?([123])",
                        ur"dot,,,":ur"dot|(水|みず)(たま|玉)",
                        ur"stripe,,,":ur"stripe|(しま|縞)(ぱん|パン|)",
                        ur"color \1,,,":ur"((\d{1,3}\s?,\s?\d{1,3}\s?,\s?\d{1,3})|[0-9a-fA-F]{6})",
                        ur"base_color \2,,,":ur"(base|ベース)\s?((\d{1,3}\s?,\s?\d{1,3}\s?,\s?\d{1,3})|[0-9a-fA-F]{6})",
                        ur"nopants,,,":ur"(nopants|のーぱん|ノーパン|(ぱんつ)?すぽーん|キャストオフ|cast\s?off)",
                        ur"sigh,,,":ur"sigh|溜息|ため息",
                        ur"angry,,,":ur"angry|怒り",
                        ur"mosaic,,,":ur"mosaic|モザイク",
                        ur"star,,,":ur"star|星|★|☆",
                        ur"sweat,,,":ur"sweat|汗",
                        ur"oval,,,":ur"oval|丸|メガネ|眼鏡|めがね|glass",
                        ur"square,,,":ur"square|四角",
                        }
        
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
        angry = Image.open(self.base_path + "/angry.png")
        mosaic = Image.open(self.base_path + "/mosaic.png")
        sigh = Image.open(self.base_path + "/sigh.png")
        star = Image.open(self.base_path + "/star.png")
        sweat = Image.open(self.base_path + "/sweat.png")
        glasses_oval = Image.open(self.base_path + "/glasses_oval.png")
        glasses_sq = Image.open(self.base_path + "/glasses_sq.png")
        self.image = {"normal":base, "pants":base_pants, "cheek":{1:cheek1, 2:cheek2, 3:cheek3},
                      "face":{1:face1, 2:face2, 3:face3, 4:face4, 5:face5, 
                              6:face6, 7:face7, 8:face8, 9:face9, 10:face10, 11:face11, 12:face12},
                       "frame":frame,
                      "ribbon":ribbon, "dot":dot, "stripe":stripe, "base_mask":base_mask,
                      "angry":angry, "mosaic":mosaic, "sweat":sweat, "sigh":sigh, "star":star,
                      "oval":glasses_oval, "square":glasses_sq,
                      }
        
        self.base_image = self.image["pants"]
        self.pattern_image = self.image["stripe"]
        self.color_image = Image.new("RGBA", (240, 240), 0x000000)
        self.base_color_image = Image.new("RGBA", (240, 240), 0xffffff)
        self.cheek_image = self.image["cheek"][1]
        self.face_image = self.image["face"][1]
        self.equip_pants = True
        
        # initialize
        self.gen_icon(u"face 4 base ffffff 00ffff dot cheek 3 眼鏡")

    def command_perser(self, text):
        ''' userstreamから受け取った文字列からコマンドを取り出し辞書で返す '''
        text = text.replace(u",,,",u"")
        for repl, pattern in self.regexp_dic.items():
            text = re.sub(pattern, repl, text)
        command_list = filter(lambda x:x!="",text.split(u",,,"))
        self.command = self._validate(command_list)
        return self.command

    def _validate(self, command_list):
        ''' commandの辞書の値が正しいかチェックする '''
        command_dict = {}
        command_dict["others"] = []
        for com in command_list:
            if "face" in com:
                num = int(re.compile("\d{1,2}").search(com).group())
                if num > 0 and num < 13:
                    if num == 10 and random() >= 0.1:
                        num = randint(1, 12)
                    command_dict["face"] = num
            
            elif "cheek" in com:
                num = int(re.compile("\d").search(com).group())
                if num == 1 or num == 2 or num == 3:
                    command_dict["cheek"] = num
            
            elif "stripe" in com:
                command_dict["pants"] = "stripe"
            elif "dot" in com:
                command_dict["pants"] = "dot"
            
            elif "base_color" in com:
                base_color_10 = re.compile("\d{1,3}\s?,\s?\d{1,3}\s?,\s?\d{1,3}").search(com)
                base_color_16 = re.compile("[0-9a-fA-F]{6}").search(com)
                if base_color_10:
                    base_color_10 = base_color_10.group()
                    base_color = tuple(map(int, base_color_10.split(',')))
                elif base_color_16:
                    base_color_16 = base_color_16.group()
                    base_color = (int(base_color_16[:2],16), int(base_color_16[2:4],16), int(base_color_16[4:6],16))
                if self._color_is_valid(base_color): # RGB範囲チェック
                    command_dict["base_color"] = base_color
            elif "color" in com:
                color_str = com.replace("color","").strip()
                if ',' in color_str: # ','区切りの色指定の場合.
                    color = tuple(map(int, color_str.split(',')))
                else: # 16進カラーコードの場合.
                    color = (int(color_str[:2],16), int(color_str[2:4],16), int(color_str[4:6],16))
                if self._color_is_valid(color): # RGB範囲チェック
                    command_dict["color"] = color
            
            elif "nopants" in com:
                command_dict["nopants"] = True
                
            else:
                command_dict["others"].append(com.strip())
        return command_dict

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
        self._gen_others()
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

    def _gen_others(self):
        for accessory in self.command["others"]:
            self.icon.paste(self.image[accessory], mask=self.image[accessory])