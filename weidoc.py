#-*- coding:utf-8 -*-

import requests
import pytesseract
import logging
import functools
import sys
import json

from bs4 import BeautifulSoup
from PIL import Image
from filter_pixel import filter_pixels

protocol = "https"
host = "www.guahao.com"
server_url = "%s://%s" % (protocol, host)


def get_validcode(image_path, img_stream_to_text_func):
        return img_stream_to_text_func(image_path).strip()


def get_validcode_by_human(path):
        sys.stdout.write("Please Input Valid Code(%s):" % path)
        validcode = sys.stdin.readline()
        return validcode


def get_validcode_by_ocr(path):
        f = Image.open(path)
        return pytesseract.image_to_string(f, lang="eng")


headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        "content-language": "zh-CN"
}

def post_login_form(s, usr, pwd, validimg_url, get_validcode_func):
        r = s.get(validimg_url, stream=True)
        cnt = r.headers['content-type']
        suffix = cnt.split('/')[-1]
        with open("validcode.%s" % suffix, 'wb') as f:
                f.write(r.content)
        r.close()

        validCode = get_validcode("validcode.%s" % suffix, get_validcode_func)
        if validCode == "":
                return None
        print "Parsed validCode: %s" % validCode

        data = {"method": "dologin",
                "target": "/",
                "loginId": usr,
                "password": pwd,
                "validCode": validCode}
        resp = s.post("%s/user/login" % server_url, data=data, headers=headers)
        if int(resp.status_code) != 200:
                print resp
                with open("err.html", 'wb') as f:
                        f.write(resp.content)
                return None

        soup = BeautifulSoup(resp.text, 'html.parser')
        return soup


def is_login_success(soup):
        if soup is None:
                print "Unknown Error"
                return False
        for span in soup.find_all('span'):
                if "验证码错误" in str(span):
                        print "validCode is not right"
                        return False
                if "系统异常" in str(span):
                        print "System Error"
                        return False
        return True


def login(server_url, usr, pwd):
        s = requests.Session()
        resp = s.get("%s/user/login" % server_url, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        validcode = ""
        for img in soup.find_all('img'):
                if "validcode" in str(img):
                        validcode = img['src']
        validimg_url = "%s%s" % (server_url, validcode)
        soup = post_login_form(s, usr, pwd, validimg_url, get_validcode_by_ocr)
        login_success = is_login_success(soup)
        i = 3
        while not login_success and i > 0:
                soup = post_login_form(s, usr, pwd, validimg_url, get_validcode_by_ocr)
                login_success = is_login_success(soup)
                i -= 1
        print "Login %s" % ("success" if login_success else "fail")
        return s

def show_shift(shift):
        print "=" * 10
        print "week: %s date: %s" % (shift['week'], shift['date'])
        print "Available: %s" % ('Yes' if shift['url'] else 'No')
        print "price %s" % shift['price']

def is_shift_avaiable(shift):
        return shift['url'] != ""

def alert_doc_available(shifts):
        for s in shifts:
                show_shift(s)


def check_doctor(s, server_url, doc_url, action):
        resp = s.get("%s/%s" % (server_url, doc_url))
        shiftinfo = json.loads(resp.text)
        # print json.dumps(shiftinfo, indent=2)
        available_shifts = []
        for shift in shiftinfo['data']["shiftSchedule"]:
                show_shift(shift)
                if is_shift_avaiable(shift):
                        available_shifts.append(shift)
        if len(available_shifts) > 0:
                action(available_shifts)

if __name__ == "__main__":
        #s = login(server_url, "", "828d21d8aeafe633da4cce1b7e6a77d3")
        s = requests.Session()
        check_doctor(s, server_url, "expert/new/shiftcase/?expertId=133422b3-c870-47be-be72-f219949997bb000&hospDeptId=125617811675219000&hospId=125336754304601000&_=1519904513481", alert_doc_available)
