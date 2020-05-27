function sendEmails() {
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = spreadsheet.getLastRow();

  for (i=2; i <= lastRow; i++) {
    var mentee = spreadsheet.getRange(i, 1).getValue();
    var mentor = spreadsheet.getRange(i, 2).getValue();
    var question = spreadsheet.getRange(i, 3).getValue();

    MailApp.sendEmail(mentor, "MP Question", question, {cc: mentee})
    Logger.log(mentee, mentor, question);
  }
}
