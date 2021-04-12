import os
import re
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchFrameException, NoSuchElementException


class newSpider:
    def __init__(self, driver: webdriver):
        """
        :param driver: WebDriver from selenium
        """
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
                login = self.driver.find_element_by_class_name("face")  # get face to login
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
        # scroll
        js = "var q=document.documentElement.scrollTop=100000"
        return self.driver.execute_script(js)

    def getTbodyList(self):
        print("getTbodyList() get Tbody list")
        return self.driver.find_elements_by_xpath('//div[@class="group-memeber"]//tbody[contains(@class,"list")]')

    def parseTbody(self, html):
        """
        Parse tbody html to get raw member list.
        :param html: input Tbody HTML
        :return: parsed member list
        """
        print("parseTbody() parse Tbody")
        memberLists = []
        for each in html:
            memberList = each.find_elements_by_xpath('tr[contains(@class,"mb mb")]')
            memberLists += memberList
        # print("memberLists length：{}".format(len(memberLists)))
        memberLists_data = []
        for each in memberLists:
            memberLists_data.append(self.parseMember(each))
        return memberLists_data

    def parseMember(self, mb):
        """
        Parse group members' info.
        :param mb: raw member info
        :return: member info as string
        """
        print("parseMember() parse member info")
        td = mb.find_elements_by_xpath('td')
        # print("td length：{}".format(len(td)))
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
        # lastTalkTime = td[8].text.strip()

        member = self.currentGroupName + "," + qq + "," + nickname + "," + nicknameInGroup
        print(member)
        return member

    def parseAndWrite(self, tbody):
        """
        parse tbody in HTML and write
        :param tbody:
        :return:
        """
        print("parseAndWrite() written")
        memberList = self.parseTbody(tbody)
        with open(self.currentFileName, 'a+', encoding="utf-8") as f:
            for each in memberList:
                f.write(str(each) + "\n")

    def parse(self):
        prelen = 0
        currentNum = 0
        qqNum = int(self.driver.find_element_by_xpath('//*[@id="groupMemberNum"]').text.strip())
        self.currentGroupName = self.driver.find_element_by_id("groupTit").text.strip()
        self.currentGroup = re.findall(r'\([0-9]*\)', self.currentGroupName)[0][1:-1]
        self.currentFileName = self.currentGroup + ".csv"
        print("Group size: " + str(qqNum))
        while currentNum != qqNum:
            currentNum = len(self.driver.find_elements_by_xpath('//*[@id="groupMember"]//td[contains(@class,"td-no")]'))
            # Scroll the screen
            self.scroll()
            # wait
            time.sleep(1)
            tList = self.getTbodyList()
            self.parseAndWrite(tList[prelen:])
            prelen = len(tList)  # update length of tList

    def exe(self):
        i = True
        while i:
            try:
                self.parse()
                i = False
            except Exception:  # I don't know which exception may be triggered. The same below.
                self.driver.navigate().refresh()
                os.remove(self.currentFileName)

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
    # webdriver.ChromeOptions().add_argument("headless") # todo: Uncomment this line will run silently.
    spider = newSpider(driver)
    spider.exe()
    print()


if __name__ == "__main__":
    main()
