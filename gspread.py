"""
Author: Chayapol Moemeng
GSpread API: https://gspread.readthedocs.io/en/latest/
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def isfloat(value):
    try:
        float(value)
        return True
    except:
        return False


class DailySheet:
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds']
        # credentials = ServiceAccountCredentials.from_json_keyfile_name('config/the1erp-gspread-service-accoun.json', scope)
        credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        gc = gspread.authorize(credentials)
        ss = gc.open_by_key('1YR8d-dscMzuZi7Qxt5ReMvCOz4ItuPOGGgIiHwXWv-c')
        self.wks = ss.worksheet('Cash Calculator')

    def readDailyCashData(self):
        wks = self.wks
        branches = self.branches
        # wks.update_acell('B13', "it's down there somewhere, let me take another look.")

        for branch in branches:
            branch.cash = wks.range(branch.cashRange)[0].value
            branch.tmb = wks.range(branch.tmbRange)[0].value
            branch.directDebit = wks.range(branch.directDebitRange)[0].value

            # re-type
            branch.cash = float(branch.cash.replace(',', ''))
            branch.tmb = float(branch.tmb.replace(',', ''))
            # print('wks.range(branch.cashRange)[0]', wks.range(branch.cashRange)[0], type(wks.range(branch.cashRange)[0]))
            # print('branch.directDebit', branch.directDebit, type(branch.directDebit))
            branch.directDebit = float(branch.directDebit if isfloat(branch.directDebit) else('' + branch.directDebit).replace(',', ''))
            # branch.directDebit = branch.directDebit if isfloat(branch.directDebit) else('' + branch.directDebit).replace(',', '')
            print('branch.directDebit', branch.directDebit, type(branch.directDebit))

            # print(branch)

    def resetCash(self):
        wks = self.wks
        branches = self.branches
        for branch in branches:
            cellList = wks.range(branch.cashCountRange)
            for cell in cellList:
                cell.value = "0"
            wks.update_cells(cellList)

    def updateDailyTMBData(self):
        wks = self.wks
        branches = self.branches
        for branch in branches:
            wks.update_acell(branch.tmbRange, branch.tmb)

    def updateDailyDirectDebitData(self):
        wks = self.wks
        branches = self.branches
        for branch in branches:
            wks.update_acell(branch.directDebitRange, branch.directDebit)


if __name__ == '__main__':


    print('Open Google Sheet')
    gs = DailySheet()

    print('Read DailyCash')
    gs.readDailyCashData()

