import sys
import sqlite3
import os
import os.path
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from docxtpl import DocxTemplate
import datetime as dt
# import db_session


class Error(QMessageBox):  # создание окна ошибки, которое будет использоваться с заменой текста
    def __init__(self, a):
        super().__init__()
        err = QMessageBox()
        err.setIcon(QMessageBox.Warning)
        err.setWindowTitle("Ошибка")
        err.setStyleSheet("""
                             QLabel {
                                 color: black;
                                 font-size: 20px;
                             }""")
        err.setText(a)
        err.exec_()


class Hello(QMainWindow):  # окно входа в программу
    def __init__(self):
        super().__init__()
        uic.loadUi('Files/ui/Hello.ui', self)
        self.pushButton.clicked.connect(self.showchoice)
        self.regBtn.clicked.connect(self.showreg)
        self.sc = Choice()
        self.sr = DoctorRegistration()

    def showchoice(self):
        global fullname1
        fullname = []
        dd1 = str(self.doctorData.text()).split()
        for i in dd1:
            fullname.append(i.capitalize())
        fullname1 = ' '.join(fullname)
        if len(dd1) < 2:
            Error('Введите фамилию, имя и отчество (при наличии)')
            return
        if len(dd1) == 2:
            dd1.append('---')
        psswrd = self.userpassword.text()
        con = sqlite3.connect("Files/Medicaments.db")
        # проверка на существование данных врача в бд и на совпадение пароля
        cur = con.cursor()
        a = cur.execute("""SELECT * FROM Doctors WHERE (surname=? AND name=? AND middlename=? AND password=?)""",
                        (dd1[0].lower(), dd1[1].lower(), dd1[2].lower(), psswrd)).fetchall()
        if a == list():
            Error('Данного врача нет в базе данных или пароль неверен')
            return

        # пропуск в программу
        self.sc.show()
        self.hide()

    def showreg(self):
        self.sr.show()


class DoctorRegistration(QMainWindow):  # окно регистрации
    def __init__(self):
        super().__init__()
        uic.loadUi('Files/ui/DoctorRegistration.ui', self)
        self.buttonBox.accepted.connect(self.save_data)
        self.buttonBox.rejected.connect(self.hide)

    def save_data(self):
        doccode = self.doccode.text()
        if doccode == 'WeR4X303':  # проверка врачебного кода
            pass
        else:
            Error('Введён неверный врачебный код')
            return

        newdd = str(self.fiodata.text()).split()
        password = self.newpassword.text()
        if password == ' ' or password == '':
            Error('Введите пароль')
            return
        if len(password) < 6:
            Error('Пароль слишком короткий')
            return
        if len(newdd) < 2:
            Error('ФИО введено некорректно')
            return

        if len(newdd) == 2:
            newdd.append('---')
        con = sqlite3.connect("Files/Medicaments.db")
        cur = con.cursor()
        a = cur.execute("""SELECT * FROM Doctors WHERE (surname=? AND name=? AND middlename=?)""",
                        (newdd[0].lower(), newdd[1].lower(), newdd[2].lower())).fetchall()

        # проверка на существование данных врача в бд
        if a == list():
            cur.execute("""INSERT INTO Doctors(surname, name, middlename, password) 
                        VALUES (?, ?, ?, ?)""", (newdd[0].lower(), newdd[1].lower(), newdd[2].lower(), password))
            con.commit()  # создание записи в бд о новом враче
        else:
            Error('Врач уже зарегистрирован')
            self.doccode.clear()
            self.fiodata.clear()
            self.newpassword.clear()
            return

        self.doccode.clear()
        self.fiodata.clear()
        self.newpassword.clear()
        self.hide()


class Choice(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Files/ui/ChoiceWindow.ui', self)
        self.searchButton.clicked.connect(self.show_sw)
        self.uchetButton.clicked.connect(self.show_uw)
        self.uw = Accounting()
        self.sw = Search()

    def show_uw(self):
        self.uw.show()

    def show_sw(self):
        self.sw.show()


class Accounting(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Files/ui/UchetWindow.ui', self)
        self.saveButton.clicked.connect(self.uchet)

    def uchet(self):
        name = str(self.newMedName.text()).lower()
        if name == '' or name == ' ':
            Error('Введите название медикамента')
            return
        if str(self.newMedDescript.toPlainText()) == '' or str(self.newMedDescript.toPlainText()) == ' ':
            Error('Введите симптомы или заболевания')
            return

        desc = str(self.newMedDescript.toPlainText())
        count = int(self.newMedCount.text())
        if count <= 0:
            Error('Количество должно быть больше нуля')
            return

        con = sqlite3.connect("Files/Medicaments.db")
        cur = con.cursor()  # проверка на существование данного медикамента в бд
        s = cur.execute("""SELECT * FROM Medicaments WHERE medicament=?""", (name, )).fetchone()
        if s is None:
            cur.execute("""INSERT INTO Medicaments(medicament, amount, description)
                        VALUES (?, ?, ?)""",
                        (name, count, desc))
            con.commit()  # создание записи о медикаменте
            self.lblusp.setText('Успешно!')
            self.newMedName.clear()
            self.newMedCount.clear()
            self.newMedDescript.clear()
        else:
            Error('Данный медикамент уже есть в базе данных')
            self.newMedName.clear()
            self.newMedCount.clear()
            self.newMedDescript.clear()
            return


class Search(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Files/ui/SearchWindow.ui', self)
        self.findButton.clicked.connect(self.search)
        self.appBtn.clicked.connect(self.appoint)
        self.recHistoryBtn.clicked.connect(self.recipe_history)
        self.modified = {}
        self.titles = None
        self.srh = RecipeHistory()

    def recipe_history(self):
        con = sqlite3.connect("Files/Medicaments.db")
        cur = con.cursor()
        result = cur.execute("""SELECT * FROM Appointments""").fetchall()
        if not result:
            Error('Рецептов ещё не было')
            return
        cur.close()
        self.srh.show()

    def search(self):
        con = sqlite3.connect("Files/Medicaments.db")
        cur = con.cursor()
        fmt = str(self.findMed.text()).lower()
        if ', ' in fmt:
            fmt = fmt.split(', ')
        elif ',' in fmt:
            fmt = fmt.split(',')
        else:
            fmt = fmt.split()
        s = []
        # реализация поиска
        for i in fmt:
            result = cur.execute("""SELECT * FROM Medicaments
                                    WHERE (description LIKE ? OR medicament LIKE ?)""",
                                 ('%' + i + '%', '%' + i + '%')).fetchall()
            if not result:
                continue
            for j in result:
                if j in s:
                    continue
                else:
                    s.append(j)

        if s == list():
            error = QMessageBox()
            error.setWindowTitle("Ошибка")
            error.setStyleSheet("""
                     QLabel {
                         min-width: 200px;
                         color: black;
                         font-size: 20px;
                     }
                     QTextEdit {
                         color: black;
                         font-size: 15px;
                     }""")
            error.setText('Запрос некорректен')
            error.setIcon(QMessageBox.Warning)
            error.setStandardButtons(QMessageBox.Ok)
            error.setDefaultButton(QMessageBox.Ok)
            error.setDetailedText(
                "Введённый вами текст не является названием или данный медикамент отсутствует в базе данных.")
            error.exec_()
            return
        self.tableWidget.setRowCount(len(s))
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(['id', 'medicament', 'amount', 'description'])
        self.titles = [description[1] for description in cur.description]
        # создание таблицы
        for i, elem in enumerate(s):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def appoint(self):  # проверка на наличие медикамента, назначаемого пациенту, в бд
        con = sqlite3.connect("Files/Medicaments.db")  # и переход в окно PatientData
        cur = con.cursor()
        global appointMedName
        appointMedName = str(self.appMedName.text())
        result = cur.execute("""SELECT * FROM Medicaments
                             WHERE medicament=?""",
                             (appointMedName, )).fetchall()
        cur.close()
        if not result:
            Error('Данный медикамент отсутствует в базе данных')
            return

        self.findMed.clear()
        self.tableWidget.clear()

        self.spd = PatientData(appointMedName)
        self.spd.show()


class RecipeHistory(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Files/ui/RecipeHistory.ui', self)
        self.closeButton.clicked.connect(self.hide)
        self.history()

    def history(self):
        con = sqlite3.connect("Files/Medicaments.db")
        cur = con.cursor()
        result = cur.execute("""SELECT * FROM Appointments""").fetchall()
        if not result:
            return
        self.histWidget.setRowCount(len(result))
        self.histWidget.setColumnCount(len(result[0]))
        self.histWidget.setHorizontalHeaderLabels(['id', 'patientsurname', 'patientname', 'patientmidname',
                                                   'medicament', 'date'])
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.histWidget.setItem(i, j, QTableWidgetItem(str(val)))


class PatientData(QMainWindow):  # окно для заполнения данных о пациенте для дальнейшей выписки ему рецепта
    def __init__(self, a):
        super().__init__()
        uic.loadUi('Files/ui/PatientData.ui', self)
        self.buttonBox.accepted.connect(self.save_results)
        self.buttonBox.rejected.connect(self.hide)
        self.a = a

    def save_results(self):
        date = '{}'.format(self.dateEdit.dateTime().toString('dd.MM.yyyy'))
        con = sqlite3.connect("Files/Medicaments.db")
        cur = con.cursor()  # уменьшение количества вещества в базе данных
        cur.execute("""UPDATE Medicaments  
                       SET amount = amount - 1
                       WHERE medicament=?""", (appointMedName, )).fetchall()
        cur.execute("""DELETE from Medicaments 
                       WHERE amount = 0""")
        con.commit()

        pdtext = str(self.patientData.text()).split()
        if len(pdtext) < 2:
            Error('Введите фамилию, имя и отчество (при наличии)')
            self.patientData.clear()
            return
        if len(pdtext) == 2:
            pdtext.append('---')
        cur.execute("""INSERT INTO Appointments(patientsurname, patientname, patientmidname, medicament, date) 
                VALUES (?, ?, ?, ?, ?)""",
                    (pdtext[0].lower(), pdtext[1].lower(), pdtext[2].lower(),
                     self.a, dt.date.today().strftime('%d.%m.%y')))
        con.commit()
        for i in range(len(pdtext)):
            pdtext[i] = pdtext[i].capitalize()
        pdtext = (' ').join(pdtext)
        cur.close()
        doctordata = fullname1
        doc = DocxTemplate('Files/Sample.docx')
        context = {  # запись данных для рецепта в файл docx
            'date': dt.date.today().strftime('%d.%m.%y'),
            'patientdata': pdtext,
            'birthdate': date,
            'doctordata': doctordata,
            'medicament': self.a.capitalize(),
            'count': str(self.spinBox.text())
        }
        doc.render(context)
        if os.path.exists(f'Files/{str(self.filename.text())}.docx'):
            os.remove(f'Files/{str(self.filename.text())}.docx')
        doc.save(f'Files/{str(self.filename.text())}.docx')
        self.patientData.clear()
        self.filename.clear()
        self.spinBox.clear()
        self.hide()


if __name__ == '__main__':
    # db_session.global_init("db/Medicaments1-.sqlite")
    app = QApplication(sys.argv)
    w = Hello()
    w.show()
    app.exec()
