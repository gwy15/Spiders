# -*- coding: utf-8 -*-

import re, time

ASS_HEADER_TPL = '''[Script Info]
ScriptType: v4.00+
Collisions: Normal
PlayResX: %(video_width)s
PlayResY: %(video_height)s

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: AcplayDefault, %(font_name)s, %(font_size)s, &H55FFFFFF, &H88FFFFFF, &H88000000, &HEE000000, -1, 0, 0, 0, 100, 100, 0.00, 0.00, 1, 1.5, 0.5, 2, 20, 20, 20, 0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
TOP_TIME = 4


    # 保存已经被占用的行 LINE_POOL[line_number] = start_time@this_line



class NicoSubtitle:

    (SCROLL, TOP, BOTTOM, NOT_SUPPORT) = range(4)
    FLASH_FONT_SIZE = 25 # office flash player font size

    def __init__(self):
        self.index = None
        self.start_seconds = None
        self.font_size = None
        self.font_color = None
        self.white_border = False
        self.style = None
        self.text = None

    def __unicode__(self):
        return u'#%05d, %d, %d, %s, %s, %s' % (
                self.index, self.style,
                self.font_size, self.font_color, self.white_border,
                self.start_seconds, self.text)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    @staticmethod
    def to_style(attr):
        if attr == 1:
            style = NicoSubtitle.SCROLL
        elif attr == 4:
            style = NicoSubtitle.BOTTOM
        elif attr == 5:
            style = NicoSubtitle.TOP
        else:
            style = NicoSubtitle.NOT_SUPPORT
        return style

    @staticmethod
    def to_rgb(integer):
        return hex(integer).upper()[2:].zfill(6)

    @staticmethod
    def to_bgr(integer):
        rgb = NicoSubtitle.to_rgb(integer)
        NicoSubtitle.to_hls(integer)
        bgr = rgb[4:6] + rgb[2:4] + rgb[0:2] # ass use bgr
        return bgr

    # HLS: Hue, Luminance, Saturation
    # H: position in the spectrum
    # L: color lightness
    # S: color saturation
    @staticmethod
    def rgb_to_hls(r, g, b):
        maxc = max(r, g, b)
        minc = min(r, g, b)
        # XXX Can optimize (maxc+minc) and (maxc-minc)
        l = (minc+maxc)/2.0
        if minc == maxc:
            return 0.0, l, 0.0
        if l <= 0.5:
            s = (maxc-minc) / (maxc+minc)
        else:
            s = (maxc-minc) / (2.0-maxc-minc)
        rc = (maxc-r) / (maxc-minc)
        gc = (maxc-g) / (maxc-minc)
        bc = (maxc-b) / (maxc-minc)
        if r == maxc:
            h = bc-gc
        elif g == maxc:
            h = 2.0+rc-bc
        else:
            h = 4.0+gc-rc
        h = (h/6.0) % 1.0
        return h, l, s
        

    @staticmethod
    def to_hls(integer):
        rgb = NicoSubtitle.to_rgb(integer)
        rgb_decimals = map(lambda x: int(x, 16), (rgb[0:2], rgb[2:4], rgb[4:6]))
        rgb_coordinates = map(lambda x: x / 255, rgb_decimals)
        hls_corrdinates = NicoSubtitle.rgb_to_hls(*rgb_coordinates)
        hls = hls_corrdinates[0] * 360, hls_corrdinates[1] * 100, hls_corrdinates[2] * 100
        return hls

    
    @staticmethod
    def need_white_border(integer):
        if integer == 0:
            return True

        hls = NicoSubtitle.to_hls(integer)
        hue, lightness = hls[0:2]
        if (hue > 30 and hue < 210) and lightness < 33:
            return True
        if (hue < 30 or hue > 210) and lightness < 66:
            return True
        return False

class AssSubtitle:
    LINE_POOL = {}
    LINE_POOL_BOTTOM = {}
    LINE_POOL_TOP = {}
    @staticmethod
    def clean():
        AssSubtitle.LINE_POOL.clear()
        AssSubtitle.LINE_POOL_BOTTOM.clear()
        AssSubtitle.LINE_POOL_TOP.clear()

    def __init__(self, nico_subtitle,
                 video_width, video_height,
                 base_font_size, line_count,
                 bottom_margin, tune_seconds, line_space):

        self.nico_subtitle = nico_subtitle
        self.video_width = video_width
        self.video_height = video_height
        self.base_font_size = base_font_size
        self.line_count = line_count
        self.bottom_margin = bottom_margin
        self.tune_seconds = tune_seconds

        self.line_space = line_space
        self.text_length = self.init_text_length()
        self.start_seconds = self.nico_subtitle.start_seconds
        self.end_seconds = self.init_end_seconds()
        self.start = self.init_start()
        self.end = self.init_end()
        self.font_size = self.init_font_size()
        (self.x1, self.y1, self.x2, self.y2) = self.init_position()
        self.styled_text = self.init_styled_text()

    @staticmethod
    def to_hms(seconds):
        if seconds < 0:
            return '0:00:00.00'

        i, d = divmod(seconds, 1)
        m, s = divmod(i, 60)
        h, m = divmod(m, 60)
        return '%d:%02d:%02d.%02d' % (h, m, s, d * 100)

    def init_text_length(self):
        return float(len(self.nico_subtitle.text))

    def init_start(self):
        return AssSubtitle.to_hms(self.start_seconds)

    def init_end_seconds(self):
        if self.nico_subtitle.style in (NicoSubtitle.TOP, NicoSubtitle.BOTTOM):
            return self.start_seconds + TOP_TIME
        return 9 + self.start_seconds

        # if self.text_length < 5:
        #     end_seconds = self.start_seconds + 7 + (self.text_length / 1.5)
        # elif self.text_length < 12:
        #     end_seconds = self.start_seconds + 7 + (self.text_length / 2)
        # else:
        #     end_seconds = self.start_seconds + 13
        # end_seconds += self.tune_seconds
        # return end_seconds

    def init_end(self):
        return AssSubtitle.to_hms(self.end_seconds)

    def init_font_size(self):
        return self.nico_subtitle.font_size - NicoSubtitle.FLASH_FONT_SIZE + self.base_font_size

    def init_position(self):

        if self.nico_subtitle.style == NicoSubtitle.SCROLL:
            x1 = self.video_width + (self.base_font_size * self.text_length) / 2
            x2 = -(self.base_font_size * self.text_length) / 2

            line_number = get_line_number(self.start_seconds, self.end_seconds, self.line_count)
            
            y = int(line_number * (self.base_font_size * (1+self.line_space)))
            print(f"line = {line_number}, y = {y}")
            y1, y2 = y, y
        elif self.nico_subtitle.style == NicoSubtitle.BOTTOM:
            x = self.video_width / 2
            line_number = get_line_number_bottom(self.start_seconds, self.end_seconds, self.line_count)
            y = self.video_height - int(line_number * (self.base_font_size * (1+self.line_space))) + self.bottom_margin

            x1, x2 = x, x
            y1, y2 = y, y
        else: # TOP
            x = self.video_width / 2
            line_number = get_line_number_top(self.start_seconds, self.end_seconds, self.line_count)
            y = int(line_number * (self.base_font_size * (1+self.line_space)))

            x1, x2 = x, x
            y1, y2 = y, y

        return (x1, y1, x2 , y2)

    def init_styled_text(self, ):
        if self.nico_subtitle.font_color == 'FFFFFF':
            color_markup = ''
        else:
            color_markup = '\\c&H%s' % self.nico_subtitle.font_color
        if self.nico_subtitle.white_border:
            border_markup = '\\3c&HFFFFFF'
        else:
            border_markup = ''
        if self.font_size == self.base_font_size:
            font_size_markup = ''
        else:
            font_size_markup = '\\fs%d' % self.font_size
        if self.nico_subtitle.style == NicoSubtitle.SCROLL:
            # print((self.x1, self.y1, self.x2, self.y2))
            style_markup = r'\move(%d, %d, %d, %d)' % (self.x1, self.y1, self.x2, self.y2)
            # print(style_markup)
        else:
            style_markup = '\\a6\\pos(%d, %d)' % (self.x1, self.y1)
        markup = ''.join([style_markup, color_markup, border_markup, font_size_markup])
        return '{%s}%s' % (markup, self.nico_subtitle.text)

    @property
    def ass_line(self):
        res = 'Dialogue: 3,%(start)s,%(end)s,AcplayDefault,,0000,0000,0000,,%(styled_text)s' % dict(
                start=self.start,
                end=self.end,
                styled_text=self.styled_text)
        # print(res)
        return res

def get_line_number(start, end, _max, mydict = AssSubtitle.LINE_POOL, delta = 2):
    ''' 返回值应该位于[1, max_number] '''
    res = -1
    for i in range(_max):
        if i not in mydict.keys(): # 没出现过这一行
            print('new at %d'%i)
            mydict[i] = start
            res = i
            break
        if start - mydict[i] > delta: # 前方弹幕出发后 2s 后跟上
            print('start = %f, linestart = %f, line = %d'%(start, mydict[i], i))
            mydict[i] = start
            res = i
            break
    if res == -1: # 没有空余，选择最优解。(最早出发的弹幕)
        print(mydict)
        minStart = 99999999
        sol = 0
        for line in mydict:
            if mydict[line] < minStart:
                sol = line
                minStart = mydict[line]
        res = sol
        mydict[sol] = start
        print('选择最优解：line = %d'%sol)
    return res + 1

def get_line_number_top(start, end, _max):
    res = get_line_number(start, end, _max, AssSubtitle.LINE_POOL_TOP, TOP_TIME + 0.1)
    return res - 1
def get_line_number_bottom(start, end, _max):
    res = get_line_number(start, end, _max, AssSubtitle.LINE_POOL_BOTTOM, TOP_TIME + 0.1)
    return res - 1

#Convert from xml string and return ass string.
def convert(input, resolution='1920:1080', font_name='黑体', font_size=36, line_count=24, bottom_margin=5, shift=0, line_space = 0.15):
    AssSubtitle.clean()
    XML_NODE_RE = re.compile('<d p="([^"]*)">([^<]*)</d>')
    nico_subtitles = []
    nico_subtitle_lines = XML_NODE_RE.findall(input)
    for line in nico_subtitle_lines:
        attributes = line[0].split(',')

        nico_subtitle = NicoSubtitle()
        nico_subtitle.start_seconds = float(attributes[0])
        nico_subtitle.style = NicoSubtitle.to_style(int(attributes[1]))
        nico_subtitle.font_size = int(attributes[2])
        nico_subtitle.font_color = NicoSubtitle.to_bgr(int(attributes[3]))
        nico_subtitle.white_border = NicoSubtitle.need_white_border(int(attributes[3]))
        #nico_subtitle.text = line[1].decode('UTF-8').replace('/n', '\\N')
        nico_subtitle.text = line[1].replace('/n', '\\N')

        if nico_subtitle.style != NicoSubtitle.NOT_SUPPORT:
            nico_subtitles.append(nico_subtitle)
    nico_subtitles.sort(key=lambda x: x.start_seconds)

    for i, nico_subtitle in enumerate(nico_subtitles):
        nico_subtitle.index = i


    video_width, video_height = map(int, resolution.split(':'))

    ass_subtitles = []
    for nico_subtitle in nico_subtitles:
        ass_subtitle = AssSubtitle(nico_subtitle,
                                    video_width, video_height,
                                    font_size, line_count,
                                    bottom_margin, shift, line_space)
        ass_subtitles.append(ass_subtitle)

    ass_lines = []
    for ass_subtitle in ass_subtitles:
        ass_lines.append(ass_subtitle.ass_line)

    ass_header = ASS_HEADER_TPL % dict(video_width=video_width,
                                        video_height=video_height,
                                        font_name=font_name,
                                        font_size=font_size)
    text = ass_header + '\n'.join(ass_lines)

    return text
