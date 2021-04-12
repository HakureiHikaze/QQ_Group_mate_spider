import os
import re
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchFrameException, NoSuchElementException


class newSpider:
    def __init__(self, driver: webdriver):
        self.currentGroup = ""
        self.currentGroupName = ""
        self.currentFileName = ""
        self.driver = driver
        driver.delete_all_cookies()
        url = "https://qun.qq.com/member.html"
        self.driver.get(url)
        time.sleep(1)
        i = True
        while i:
            try:
                self.driver.switch_to.frame("login_frame")
                login = self.driver.find_element_by_class_name("face")  # 获取头像登录按键
                login.click()
                time.sleep(3)
                li_list = self.find_ul_element()
                li_list[0].click()
                i = False
            except (NoSuchFrameException, NoSuchElementException):
                self.driver.navigate().refresh()
        self.switch = self.driver.find_element_by_id("changeGroup")

    def find_ul_element(self):
        ul1 = self.driver.find_element_by_xpath("/html/body/div[5]/div[2]/div/div[2]/ul[1]")
        ul2 = self.driver.find_element_by_xpath("/html/body/div[5]/div[2]/div/div[2]/ul[2]")
        ul3 = self.driver.find_element_by_xpath("/html/body/div[5]/div[2]/div/div[2]/ul[3]")
        li_list = ul1.find_elements_by_xpath("li")
        li_list.extend(ul2.find_elements_by_xpath("li"))
        li_list.extend(ul3.find_elements_by_xpath("li"))
        return li_list

    def scroll(self):
        # 滚动条下拉
        js = "var q=document.documentElement.scrollTop=100000"
        return self.driver.execute_script(js)

    def getTbodyList(self):
        print("getTbodyList()获取Tbody列表")
        return self.driver.find_elements_by_xpath('//div[@class="group-memeber"]//tbody[contains(@class,"list")]')

    def parseTbody(self, html):
        """
        解析tbody里面的内容，一个tbody里面有多个成员，
        解析完成后，返回成员基本情况的列表
        :param html:
        :return:
        """
        print("parseTbody()解析Tbody")
        memberLists = []
        for each in html:
            memberList = each.find_elements_by_xpath('tr[contains(@class,"mb mb")]')
            memberLists += memberList
        # print("memberLists长度为：{}".format(len(memberLists)))
        memberLists_data = []
        for each in memberLists:
            memberLists_data.append(self.parseMember(each))
        return memberLists_data

    def parseMember(self, mb):
        """
        解析每个人各项描述，以逗号隔开，返回一个成员的基本情况
        :param mb:
        :return:
        """
        print("parseMember()解析成员信息")
        td = mb.find_elements_by_xpath('td')
        # print("td长度为：{}".format(len(td)))
        nickname = td[2].find_element_by_xpath('span').text.strip()
        nicknameInGroup = td[3].find_element_by_xpath('span').text.strip()
        qq = td[4].text.strip()
        # qId = td[1].text.strip()
        # nickName = td[2].find_element_by_xpath('span').text.strip()
        # card = td[3].find_element_by_xpath('span').text.strip()
        # qq = td[4].text.strip()
        # sex = td[5].text.strip()
        # qqAge = td[6].text.strip()
        # joinTime = td[7].text.strip()
        # lastTime = td[8].text.strip()

        # 1序号，2昵称，3群名片，4QQ号，5性别，6Q龄，7入群时间，8最后发言时间

        member = (self.currentGroupName + "," + qq + "," + nickname + "," + nicknameInGroup)
        print(member)
        return member

    def parseAndWrite(self, tbody):
        """
        解析HTML中的tbody，解析完成后写入到本地文件
        :param tbody:
        :return:
        """
        print("parseAndWrite()写入文件")
        memberList = self.parseTbody(tbody)
        with open(self.currentFileName, 'a+', encoding="utf-8") as f:  # 如果分析群名带windows禁止作为文件名的字符的群，
            for each in memberList:  # 则会出错，但不会引发异常。如出错，将groupName改成qqgroup
                f.write(str(each) + "\n")

    def parse(self):
        prelen = 0
        currentNum = 0
        qqNum = int(self.driver.find_element_by_xpath('//*[@id="groupMemberNum"]').text.strip())
        self.currentGroupName = self.driver.find_element_by_id("groupTit").text.strip()
        self.currentGroup = re.findall(r'\([0-9]*\)', self.currentGroupName)[0][1:-1]
        self.currentFileName = self.currentGroup + ".csv"
        print("群人数: " + str(qqNum))
        while currentNum != qqNum:
            currentNum = len(self.driver.find_elements_by_xpath('//*[@id="groupMember"]//td[contains(@class,"td-no")]'))
            # 向下滚动屏幕，直到底部
            self.scroll()
            # 每次滚动休息1秒
            time.sleep(1)
            tList = self.getTbodyList()
            self.parseAndWrite(tList[prelen:])
            prelen = len(tList)  # 更新tbody列表的长度

    def exe(self):
        self.parse()
        li_list = self.find_ul_element()
        for j in range(1, len(li_list)):
            i = True
            while i:
                try:
                    self.switch.click()
                    li_list = self.find_ul_element()
                    li_list[j].click()
                    time.sleep(1)
                    self.parse()
                    i = False
                except Exception:
                    self.driver.navigate().refresh()
                    os.remove(self.currentFileName)
        self.driver.quit()


def main():
    driver = webdriver.Chrome()
    # webdriver.ChromeOptions().add_argument("headless")
    spider = newSpider(driver)
    spider.exe()
    print()


if __name__ == "__main__":
    main()
